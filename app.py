import os
import json
import datetime
import logging

from flask import Flask, request
from telegram import Bot, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Telegram Bot Token (make sure it's stored in environment for security)
TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)

# Initialize Flask App
app = Flask(__name__)

# Simple In-Memory Database (for demonstration; use Replit DB or Redis for production)
user_data = {}

# Menu keyboard
main_menu = [["📚 Courses", "💡 Trial"], ["📈 Progress", "❌ Exit"]]

# ===== Telegram Bot Logic =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        user_data[user_id] = {
            "trial_used": False,
            "subscribed": False,
            "joined": str(datetime.datetime.now())
        }

    await update.message.reply_text(
        "👋 Welcome to SmartSkill Bot!\n\nChoose an option:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if text == "📚 Courses":
        if user_data.get(user_id, {}).get("subscribed", False):
            await update.message.reply_text("✅ Access granted. Choose a course:")
        else:
            await update.message.reply_text("🔒 Please subscribe to access courses.")
    elif text == "💡 Trial":
        if not user_data.get(user_id, {}).get("trial_used", False):
            user_data[user_id]["trial_used"] = True
            await update.message.reply_text("🎉 Trial activated! Enjoy your free session.")
        else:
            await update.message.reply_text("⚠️ Trial already used.")
    elif text == "📈 Progress":
        joined = user_data.get(user_id, {}).get("joined", "Unknown")
        await update.message.reply_text(f"📅 You joined on {joined}")
    elif text == "❌ Exit":
        await update.message.reply_text("👋 Bye! Send /start to begin again.",
                                        reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("❓ Invalid option. Please choose from the menu.")

# ===== Flask Webhook Endpoint =====

@app.route('/')
def home():
    return "SmartSkill Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return 'ok'

# ===== Bot Runner =====

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    application.run_polling()
