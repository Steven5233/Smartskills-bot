import os from flask import Flask, request from telegram import Bot, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, ApplicationBuilder import datetime import logging import json

--- Configurations ---

TOKEN = os.getenv("BOT_TOKEN") or "YOUR_TELEGRAM_BOT_TOKEN" SUBSCRIPTION_LINK = "https://linusteven.gumroad.com/l/ritlag" TRIAL_LIMIT = 3 TRIAL_RESET_DAYS = 7

In-memory database (for simplicity)

users = {}

app = Flask(name)

--- Logger ---

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

--- Bot UI Menus ---

main_menu = [ ["📚 Courses", "🧠 Learn Anything"], ["🎓 Student Help", "👤 My Profile"] ]

course_menu = [ ["Cybersecurity", "Software Engineering"], ["Business"], ["⬅️ Back to Menu"] ]

cyber_roles = [ ["🔓 Ethical Hacking", "🧪 Penetration Testing"], ["🔬 Forensics", "🛡️ Security Architect"], ["⬅️ Back"] ]

software_roles = [ ["💻 Frontend Dev", "🖥 Backend Dev"], ["📱 Mobile Dev", "🧠 AI Dev"], ["⬅️ Back"] ]

business_roles = [ ["📈 Marketing", "💼 Management"], ["📊 Analytics", "💡 Startup Guide"], ["⬅️ Back"] ]

--- Sample Topics ---

topics = { "🔓 Ethical Hacking": ["What is Ethical Hacking?", "Phases of PenTesting", "Common Tools"], "💻 Frontend Dev": ["HTML & CSS", "JavaScript", "React Basics"], "📈 Marketing": ["Social Media", "Email Campaigns", "SEO"] }

--- Helper Functions ---

def is_subscribed(user_id): user = users.get(user_id, {}) return user.get("subscribed", False)

def check_trial(user_id): user = users.setdefault(user_id, {"trial": 0, "last_reset": str(datetime.date.today()), "subscribed": False}) last_reset = datetime.date.fromisoformat(user["last_reset"]) if (datetime.date.today() - last_reset).days >= TRIAL_RESET_DAYS: user["trial"] = 0 user["last_reset"] = str(datetime.date.today()) return user["trial"] < TRIAL_LIMIT

--- Command Handlers ---

async def start(update: Update, context: CallbackContext): user_id = update.effective_user.id users.setdefault(user_id, {"trial": 0, "last_reset": str(datetime.date.today()), "subscribed": False}) await update.message.reply_text( f"👋 Welcome to SmartSkill Bot!\n\nAccess expert-led courses in Cybersecurity, Software Engineering, and Business.\n\n💡 Try any 3 topics for FREE!\n🔒 To unlock full access, subscribe here:\n{SUBSCRIPTION_LINK}", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True) )

async def handle_message(update: Update, context: CallbackContext): user_id = update.effective_user.id text = update.message.text

if text == "📚 Courses":
    await update.message.reply_text("Choose a course:", reply_markup=ReplyKeyboardMarkup(course_menu, resize_keyboard=True))

elif text == "Cybersecurity":
    await update.message.reply_text("Select a Cybersecurity path:", reply_markup=ReplyKeyboardMarkup(cyber_roles, resize_keyboard=True))

elif text == "Software Engineering":
    await update.message.reply_text("Choose a Software Engineering role:", reply_markup=ReplyKeyboardMarkup(software_roles, resize_keyboard=True))

elif text == "Business":
    await update.message.reply_text("Pick a Business path:", reply_markup=ReplyKeyboardMarkup(business_roles, resize_keyboard=True))

elif text == "⬅️ Back to Menu":
    await update.message.reply_text("Returning to main menu:", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))

elif text == "⬅️ Back":
    await update.message.reply_text("Choose a course:", reply_markup=ReplyKeyboardMarkup(course_menu, resize_keyboard=True))

elif text in topics:
    user = users[user_id]
    if is_subscribed(user_id) or check_trial(user_id):
        if not is_subscribed(user_id):
            users[user_id]["trial"] += 1
        await update.message.reply_text(f"📘 Learning path for {text}:")
        for t in topics[text]:
            await update.message.reply_text(f"• {t}")
        if not is_subscribed(user_id):
            await update.message.reply_text(f"🔒 Trial used: {users[user_id]['trial']} of {TRIAL_LIMIT}")
            if users[user_id]["trial"] >= TRIAL_LIMIT:
                await update.message.reply_text(f"⚠️ Your trial has ended. Subscribe here to unlock all courses:\n{SUBSCRIPTION_LINK}")
    else:
        await update.message.reply_text(f"🚫 Your free trial is over. Subscribe to continue:\n{SUBSCRIPTION_LINK}")

elif text == "🎓 Student Help":
    await update.message.reply_text("Send me your assignment or project topic. I’ll help you understand, write, and solve it.")

elif text == "🧠 Learn Anything":
    await update.message.reply_text("Type anything you want to learn about. For example: 'Explain Quantum Computing' or 'Teach me Python'")

elif text == "👤 My Profile":
    user = users.get(user_id, {})
    subscribed = "✅ Subscribed" if user.get("subscribed") else "❌ Not Subscribed"
    await update.message.reply_text(f"📄 Profile Info:\n• Subscription: {subscribed}\n• Trial used: {user.get('trial', 0)} / {TRIAL_LIMIT}")

else:
    await update.message.reply_text("Processing your request...")
    await update.message.reply_text(f"🤖 Learning: {text}\n(This is a demo response powered by ChatGPT.)")

--- Webhook for Gumroad ---

@app.route("/gumroad", methods=["POST"]) def gumroad_webhook(): data = request.form email = data.get("email") if not email: return "Missing email", 400 for uid, udata in users.items(): if udata.get("email") == email: udata["subscribed"] = True return "OK", 200

--- Telegram Bot Setup ---

async def main(): app_builder = ApplicationBuilder().token(TOKEN).build() app_builder.add_handler(CommandHandler("start", start)) app_builder.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) await app_builder.initialize() await app_builder.start() print("🤖 SmartSkill Bot running...") await app_builder.updater.start_polling() await app_builder.updater.idle()

if name == 'main': import asyncio from threading import Thread Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start() asyncio.run(main())

