
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import requests

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

GENDER, COUNT = range(2)

gender_keyboard = [["🧑‍🎨 ប្រុស", "👩‍🎨 ស្រី"]]
count_keyboard = [["1", "5", "10"]]

BOT_TOKEN = os.getenv("BOT_TOKEN")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_API_SECRET = os.getenv("RUNPOD_API_SECRET")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "សូមជ្រើសរើសភេទ៖",
        reply_markup=ReplyKeyboardMarkup(gender_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text(
        "សូមជ្រើសរើសចំនួនរូប៖",
        reply_markup=ReplyKeyboardMarkup(count_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return COUNT

async def count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text)
        gender = context.user_data.get("gender", "")
        is_male = "ប្រុស" in gender

        await update.message.reply_text("⏳ កំពុងបង្កើតរូប... សូមរងចាំ...", reply_markup=ReplyKeyboardRemove())

        for i in range(count):
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

            logging.info(f"RunPod API response {i+1}: {response.text}")
            data = response.json()
            image_url = data.get("output", {}).get("image_url")
            if image_url:
                await update.message.reply_photo(photo=image_url)
            else:
                await update.message.reply_text(f"❌ រូបទី {i+1} មិនទាន់បង្កើតបានទេ!")

    except Exception as e:
        logging.error(f"Exception: {e}")
        await update.message.reply_text("❌ មានបញ្ហាកើតឡើងក្នុងការបង្កើតរូប។")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("បានបោះបង់!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, count)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    run_bot()
