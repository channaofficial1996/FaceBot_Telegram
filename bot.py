import os
import requests
import zipfile
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_API_SECRET = os.getenv("RUNPOD_API_SECRET")

reply_keyboard = [['🧑‍🎨 បុរស', '👩‍🎨 ស្រី']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("សូមជ្រើសរើសភេទ:", reply_markup=markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['gender'] = 'male' if 'បុរស' in text else 'female' if 'ស្រី' in text else None

    if context.user_data.get('gender'):
        await update.message.reply_text("📸 តើអ្នកចង់បានរូបប៉ុន្មាន?", reply_markup=ReplyKeyboardMarkup(
            [['1', '5', '10']], one_time_keyboard=True, resize_keyboard=True))
    elif text in ['1', '5', '10'] and context.user_data.get('gender'):
        quantity = int(text)
        gender = context.user_data['gender']
        await update.message.reply_text("⏳ កំពុងបង្កើតរូប... សូមមេត្តារងចាំ")

        images = []
        for i in range(quantity):
            prompt = f"face only portrait of a {gender} person, white background, 1080x1080, clean, AI generated"
            headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}"}
            res = requests.post("https://api.runpod.ai/v2/realistic-vision-v51/run", json={"input": {"prompt": prompt}}, headers=headers)

            try:
                output_url = res.json()['output'][0]
                img_data = requests.get(output_url).content
                file_path = f"/mnt/data/{gender}_{i}.png"
                with open(file_path, 'wb') as f:
                    f.write(img_data)
                images.append(file_path)
            except Exception:
                await update.message.reply_text("❌ មិនអាចទាញយករូបបានទេ!")
                return

        if quantity < 50:
            for img_path in images:
                await update.message.reply_photo(photo=open(img_path, 'rb'))
        else:
            zip_path = f"/mnt/data/{gender}_faces.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img_path in images:
                    zipf.write(img_path, arcname=os.path.basename(img_path))
            await update.message.reply_document(document=open(zip_path, 'rb'))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
