import os import json import datetime import logging

from flask import Flask, request from telegram import ( Bot, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ) from telegram.ext import ( ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, )

app = Flask(name)

Bot Token and Payment Link

TOKEN = os.getenv("BOT_TOKEN") PAYMENT_LINK = "https://linusteven.gumroad.com/l/ritlag" TRIAL_LIMIT = 3 TRIAL_RESET_DAYS = 7

In-memory DB simulation (you should use a real DB)

users_db = {} learning_paths = { "Cybersecurity": [ "Ethical Hacking", "Computer Forensics", "Cybersecurity Engineer", "Security Architect" ], "Software Engineering": [ "Frontend Developer", "Backend Developer", "Full Stack", "DevOps Engineer" ], "Business": [ "Digital Marketing", "Entrepreneurship", "Business Analytics", "E-commerce" ] }

@app.route("/") def index(): return "SmartSkill Bot is Live!"

@app.route(f"/{TOKEN}", methods=["POST"]) def telegram_webhook(): update = Update.de_json(request.get_json(force=True), bot) application.update_queue.put(update) return "ok"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = str(update.message.chat_id) users_db.setdefault(user_id, {"trials": 0, "last_trial": None, "subscribed": False})

keyboard = [["Cybersecurity", "Software Engineering"], ["Business"], ["Help"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
await update.message.reply_text(
    "👋 Welcome to SmartSkill Bot!\n\nChoose a course to get started:",
    reply_markup=reply_markup
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = str(update.message.chat_id) message = update.message.text

user_data = users_db.get(user_id, {})

if message in learning_paths:
    roles = learning_paths[message]
    buttons = [[role] for role in roles]
    buttons.append(["Back to Menu"])
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(f"Select your preferred role in {message}:", reply_markup=reply_markup)
    return

elif message in sum(learning_paths.values(), []):
    # Trial logic
    trials = user_data.get("trials", 0)
    last_trial = user_data.get("last_trial")
    subscribed = user_data.get("subscribed", False)

    if subscribed:
        await update.message.reply_text(f"📘 Starting course on {message}...\n\n[Lesson 1] ...")
    else:
        if trials < TRIAL_LIMIT:
            users_db[user_id]["trials"] += 1
            users_db[user_id]["last_trial"] = datetime.datetime.now().isoformat()
            await update.message.reply_text(f"🎓 Trial {trials+1}/{TRIAL_LIMIT}\n\n[Lesson 1] {message} content here...")
        else:
            await update.message.reply_text(f"🚫 Trial limit reached. Please subscribe to continue:\n{PAYMENT_LINK}")

elif message == "Help":
    await update.message.reply_text("📚 Use the buttons to navigate and start learning.\nYou have 3 free trials per week.")

elif message == "Back to Menu":
    await start(update, context)
else:
    await update.message.reply_text("❓ Please select a valid option from the menu.")

@app.route("/gumroad-webhook", methods=["POST"]) def gumroad_webhook(): data = request.form if data.get("purchase" or {}).get("email"): email = data["purchase"]["email"] # Optional: You may map email to Telegram ID if collected for uid in users_db: if users_db[uid].get("email") == email: users_db[uid]["subscribed"] = True return "Webhook received"

Logging

logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO )

Bot Setup

bot = Bot(token=TOKEN) application = ApplicationBuilder().token(TOKEN).build() application.add_handler(CommandHandler("start", start)) application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

Start bot in background (for Render)

if name == "main": import threading threading.Thread(target=application.run_polling).start() app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

