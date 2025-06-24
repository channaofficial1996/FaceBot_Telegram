
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_API_SECRET = os.getenv("RUNPOD_API_SECRET")

# Auto-delete webhook
def delete_webhook(token):
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    try:
        response = requests.post(url)
        print("Webhook delete response:", response.json())
    except Exception as e:
        print("Error deleting webhook:", e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running with V1.4 and auto webhook clear!")

def main():
    delete_webhook(TOKEN)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
