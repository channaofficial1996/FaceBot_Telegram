
import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import requests
import uuid
from pathlib import Path

logging.basicConfig(level=logging.INFO)

# States
GENDER, COUNT = range(2)

# Keyboard buttons
gender_keyboard = [["🧑‍🎨 ប្រុស", "👩‍🎨 ស្រី"]]
count_keyboard = [["1", "5", "10"]]

# Environment variables
BOT_TOKEN = os.getenv("7942349035:AAG81GZeNw5-daNz8rHOSG6shxx2D14HCsA")
RUNPOD_API_KEY = os.getenv("user_2yxWJm4DyLIB69789HCyKWrWPrT")
RUNPOD_API_SECRET = os.getenv("rps_QDCZANA9QSBRO7F9GZYA55ZB1ZXAH0YKI9NTLSLCqu5cjg")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("សូមជ្រើសរើសភេទ:", reply_markup=ReplyKeyboardMarkup(gender_keyboard, one_time_keyboard=True))
    return GENDER

# Gender handler
async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text("ចូលចិត្តចំនួនរូបប៉ុន្មាន?", reply_markup=ReplyKeyboardMarkup(count_keyboard, one_time_keyboard=True))
    return COUNT

# Count handler
async def count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = int(update.message.text)
    gender = context.user_data["gender"]
    is_male = "ប្រុស" in gender

    image_urls = []
    for _ in range(count):
        response = requests.post(
            "https://api.runpod.ai/v2/stable-diffusion-v1/run",
            headers={"Authorization": f"Bearer {RUNPOD_API_KEY}"},
            json={"input": {
                "prompt": f"{'handsome male face' if is_male else 'beautiful female face'}, white background, centered headshot, 1080x1080",
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
                "size": "1080x1080"
            }}
        )
        data = response.json()
        image_url = data.get("output", {}).get("image_url")
        if image_url:
            image_urls.append(image_url)

    for url in image_urls:
        await update.message.reply_photo(photo=url)

    return ConversationHandler.END

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("បោះបង់ការជ្រើសរើស។")
    return ConversationHandler.END

# Bot runner
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, count)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    run_bot()
    
