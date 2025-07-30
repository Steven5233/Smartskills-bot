import os
import json
import requests
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ------------------ CONFIG ------------------
TOKEN = os.getenv(
          8205667394:AAE6WW3RdfInZXdXMN9fwJ1G1PhiCXzOHCE
         )
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GUMROAD_PRODUCT_ID = "ritlag"
GUMROAD_API_URL = "https://api.gumroad.com/v2/sales"
GUMROAD_ACCESS_TOKEN = os.getenv("GUMROAD_ACCESS_TOKEN")
GUMROAD_PAYMENT_LINK = "https://linusteven.gumroad.com/l/ritlag"
BOT_OWNER = "Adoyi Steven"
POWERED_BY = "ChatGPT"

# ------------------ FLASK APP ------------------
app = Flask(__name__)

# ------------------ DATA ------------------
USERS = {}
COURSES = {
    "Cybersecurity": [
        "Introduction to Cybersecurity",
        "Network Security Basics",
        "Ethical Hacking Tools"
    ],
    "Software Engineering": [
        "Software Development Life Cycle",
        "Agile and Scrum",
        "Design Patterns"
    ],
    "Business": [
        "Starting a Business",
        "Marketing 101",
        "Financial Planning"
    ]
}

# ------------------ UTIL ------------------
def check_gumroad_email(email):
    params = {
        "access_token": GUMROAD_ACCESS_TOKEN,
        "product_permalink": GUMROAD_PRODUCT_ID
    }
    response = requests.get(GUMROAD_API_URL, params=params)
    if response.status_code == 200:
        sales = response.json().get("sales", [])
        return any(sale.get("email") == email for sale in sales)
    return False

# ------------------ TELEGRAM HANDLERS ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    USERS.setdefault(user_id, {"trial": True, "email": None})

    keyboard = [["Courses"], ["Student Assistant"], ["Learn Anything"], ["Subscription Info"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        f"👋 Welcome to SmartSkill Bot!\n"
        f"Learn and grow with professional courses.\n\n"
        f"🧠 Powered by {POWERED_BY}\n👤 Owner: {BOT_OWNER}",
        reply_markup=reply_markup
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await update.message.reply_text("❌ Usage: /verify your_email@example.com")
        return

    email = args[0]
    if check_gumroad_email(email):
        USERS[user_id]["email"] = email
        USERS[user_id]["email_verified"] = True
        USERS[user_id]["trial"] = False
        await update.message.reply_text("✅ Subscription verified! You now have full access.")
    else:
        await update.message.reply_text("❌ Email not found in Gumroad sales. Please check or contact support.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    user_data = USERS.get(user_id, {})

    if text == "Courses":
        if not user_data.get("trial") and not user_data.get("email_verified"):
            await update.message.reply_text("❌ Please subscribe first: " + GUMROAD_PAYMENT_LINK)
            return
        courses = "\n".join([f"📘 {c}" for c in COURSES.keys()])
        await update.message.reply_text(f"📚 Available Courses:\n{courses}\n\nType course name to continue.")

    elif text in COURSES:
        topics = COURSES[text]
        await update.message.reply_text(
            f"📘 *{text} Topics:*\n- " + "\n- ".join(topics),
            parse_mode="Markdown"
        )

    elif text == "Student Assistant":
        await update.message.reply_text("📚 Send me your course, assignment or project and I'll help you solve it.")

    elif text == "Learn Anything":
        await update.message.reply_text("🤖 What do you want to learn today? Just type it!")

    elif text == "Subscription Info":
        if user_data.get("email_verified"):
            await update.message.reply_text("✅ You are subscribed!")
        else:
            await update.message.reply_text(
                f"💡 To unlock all features, subscribe here: {GUMROAD_PAYMENT_LINK}\n"
                f"After payment, send /verify your_email@example.com"
            )
    else:
        await update.message.reply_text("✅ Received! Our AI is working on your request.")

# ------------------ SETUP BOT ------------------
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("verify", verify))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ------------------ WEBHOOK ENDPOINT ------------------
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def root():
    return "SmartSkill Bot is live!"

# ------------------ STARTUP ------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(application.bot.set_webhook(f"{WEBHOOK_URL}/webhook/{TOKEN}"))
    app.run(host="0.0.0.0", port=10000)
