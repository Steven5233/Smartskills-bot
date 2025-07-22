import os
import json
import datetime
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

# Get bot token from environment variable
TOKEN = os.environ.get("BOT_TOKEN")

# Simple in-memory database (for demo; use real DB for production)
user_data = {}

# Telegram bot app
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Menu
main_menu = [["📚 Courses", "💡 Trial"], ["📈 Progress", "❌ Exit"]]

# Telegram bot commands
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
            await update.message.reply_text(
                "🔒 Please subscribe here to access courses:\n\n"
                "👉 https://linusteven.gumroad.com/l/ritlag"
            )
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

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask root
@app.route('/')
def index():
    return "SmartSkill Bot is Live!"

# Telegram webhook
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# Entry point for local test (not used in Render)
if __name__ == '__main__':
    import asyncio
    async def run():
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
    asyncio.run(run())
