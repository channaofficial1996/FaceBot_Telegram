
import os
import requests
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("BOT_TOKEN")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_API_SECRET = os.getenv("RUNPOD_API_SECRET")
GENDER, AMOUNT = range(2)

reply_keyboard = [['🧑‍🎨 Male Face', '👩‍🎨 Female Face']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("សូមជ្រើសរើសភេទរូបភាព:", reply_markup=markup)
    return GENDER

async def gender_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = 'male' if 'Male' in update.message.text else 'female'
    context.user_data['gender'] = gender
    await update.message.reply_text("📌 បញ្ចូលចំនួនរូបៈ 1 / 5 / 10")
    return AMOUNT

async def amount_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = int(update.message.text.strip())
    gender = context.user_data.get('gender', 'male')
    await update.message.reply_text("⌛ កំពុងបង្កើតរូប... សូមមេត្តរងចាំ...")

    url = "https://api.runpod.ai/v1/stable-diffusion-v1/run"
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_SECRET}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "prompt": f"1080x1080 portrait photo of {gender} face, white background, closeup, realistic",
            "num_outputs": amount
        }
    }

    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200 and 'output' in response.json():
                images = response.json()['output']
                for img_url in images:
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_url)
                await update.message.reply_text(f"✅ បង្កើតរូប {amount} រូបសម្រាប់ {gender} សម្រេច")
                break
            else:
                raise ValueError("Empty output or failed response")
        except Exception as e:
            if attempt == 2:
                await update.message.reply_text("❌ បរាជ័យក្នុងការទាញរូប! សូមសាកល្បងម្ដងទៀត.")
            else:
                time.sleep(2)
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_chosen)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_chosen)]
        },
        fallbacks=[]
    )
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
