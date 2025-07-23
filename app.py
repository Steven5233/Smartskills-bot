# Import standard libraries
import os
import logging
import asyncio

# Import third-party libraries
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get tokens from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GUMROAD_API_KEY = os.getenv("GUMROAD_API_KEY")  # Optional

# Define user data structure
user_db = {}

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username

    # Check if user already exists
    if user_id not in user_db:
        # Grant free trial
        user_db[user_id] = {"status": "trial", "username": username}
        await update.message.reply_text(
            f"👋 Welcome {username}! You’re on a free trial.\n\nChoose a course to begin:",
            reply_markup=ReplyKeyboardMarkup(
                [["Cybersecurity", "Programming"], ["Fitness", "Business"]],
                resize_keyboard=True
            )
        )
    else:
        await update.message.reply_text(
            f"👋 Welcome back {username}!",
            reply_markup=ReplyKeyboardMarkup(
                [["Cybersecurity", "Programming"], ["Fitness", "Business"]],
                resize_keyboard=True
            )
        )

# Handle course selection
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Cybersecurity":
        await update.message.reply_text("🔐 Starting Cybersecurity course...")
    elif text == "Programming":
        await update.message.reply_text("💻 Starting Programming course...")
    elif text == "Business":
        await update.message.reply_text("📈 Starting Business course...")
    elif text == "Fitness":
        await update.message.reply_text("💪 Starting Fitness course...")
    else:
        await update.message.reply_text("❓ Unknown choice. Please select a valid course.")

# Main bot function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    print("✅ Bot is running...")
    await app.run_polling()

# Run bot
if __name__ == '__main__':
    asyncio.run(main())
