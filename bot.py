import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_API_SECRET = os.getenv("RUNPOD_API_SECRET")

keyboard_main = [["🧑‍🎨 Male Face", "👩‍🎨 Female Face"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("សូមជ្រើសរើសភេទ:", reply_markup=ReplyKeyboardMarkup(keyboard_main, resize_keyboard=True))

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = "male" if "Male" in update.message.text else "female"
    await update.message.reply_text("📌 បញ្ជូលចំនួនរូប៖ 1 / 5 / 10")

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text not in ["1", "5", "10"]:
        await update.message.reply_text("❌ ចំនួនមិនត្រឹមត្រូវ")
        return
    amount = int(update.message.text)
    gender = context.user_data.get("gender", "male")
    await update.message.reply_text("⏳ កំពុងបង្កើតរូប... សូមរងចាំ...")

    # Fake response for now
    await update.message.reply_text(f"✅ បង្កើតរូប {amount} រូបសម្រាប់ {gender} សម្រេច")

def delete_webhook():
    if not BOT_TOKEN:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    except Exception:
        pass

def run_bot():
    delete_webhook()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(🧑‍🎨 Male Face|👩‍🎨 Female Face)$"), handle_gender))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount))
    app.run_polling()

if __name__ == "__main__":
    run_bot()
