Import standard libraries

import os import datetime import json

Import Flask for web server

from flask import Flask, request

Import Telegram Bot API

from telegram import Bot from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

Import Gumroad and HTTP

import requests

Import threading for async behavior

import threading

Create a Flask app instance

app = Flask(name)

======================

Set your bot token and Gumroad product details

======================

Telegram bot token

BOT_TOKEN = os.getenv("BOT_TOKEN", "your_telegram_bot_token")

Gumroad product checkout link (monthly subscription)

GUMROAD_LINK = "https://linusteven.gumroad.com/l/ritlag"

Set your authorized user IDs (for testing and admin control)

ADMIN_IDS = [123456789]  # Replace with your Telegram user ID

Create the bot instance

bot = Bot(token=BOT_TOKEN)

Define the command: /start

async def start(update, context): user_id = update.effective_user.id welcome_text = ( "Welcome to SmartSkills Bot!\n\n" "📚 Available Courses:\n" "- Cybersecurity\n" "- Programming\n" "- Software Engineering\n" "- Affiliate Marketing\n" "- Business\n" "- Diet & Fitness\n\n" "💡 Use /subscribe to access all courses.\n" "🎯 You can explore topics, track progress, and more!" ) await update.message.reply_text(welcome_text)

Define the command: /subscribe

async def subscribe(update, context): user_id = update.effective_user.id sub_text = ( "To access all SmartSkill courses, please subscribe using the link below: \n\n" f"🔗 {GUMROAD_LINK}" ) await update.message.reply_text(sub_text)

Define command: /courses

async def courses(update, context): course_list = ( "Available Courses:\n" "1. Cybersecurity Basics\n" "2. Ethical Hacking\n" "3. Python Programming\n" "4. Software Engineering Principles\n" "5. Affiliate Marketing Guide\n" "6. Business and Startup Tips\n" "7. Diet and Fitness Plan\n" "\nUse /learn <course_number> to begin." ) await update.message.reply_text(course_list)

Define the learning command: /learn <course_number>

async def learn(update, context): args = context.args if not args: await update.message.reply_text("Please use the format /learn <course_number>") return

course_map = {
    "1": "Cybersecurity Basics:\n- What is Cybersecurity\n- Threat Types\n- Tools & Techniques",
    "2": "Ethical Hacking:\n- Reconnaissance\n- Scanning & Enumeration\n- Exploitation & Reporting",
    "3": "Python Programming:\n- Variables\n- Loops\n- Functions\n- Projects",
    "4": "Software Engineering:\n- SDLC\n- Agile/DevOps\n- System Design",
    "5": "Affiliate Marketing:\n- Choosing a Niche\n- Traffic Sources\n- Conversion Optimization",
    "6": "Business Tips:\n- Startup Models\n- Funding\n- Scaling Strategies",
    "7": "Diet & Fitness:\n- Diet Plans\n- Workout Routines\n- Daily Habits"
}

course_number = args[0]
content = course_map.get(course_number, "Invalid course number.")
await update.message.reply_text(content)

Define fallback handler for unknown messages

async def unknown(update, context): await update.message.reply_text("Sorry, I didn't understand that command. Use /start to begin.")

Flask route to keep the Render server alive

@app.route('/') def home(): return "SmartSkills Bot is running!"

Flask webhook route (for Telegram webhooks, if used)

@app.route('/webhook', methods=['POST']) def webhook(): return "OK"

Run the Telegram bot in a separate thread

async def run_bot(): app_builder = ApplicationBuilder().token(BOT_TOKEN).build()

app_builder.add_handler(CommandHandler("start", start))
app_builder.add_handler(CommandHandler("subscribe", subscribe))
app_builder.add_handler(CommandHandler("courses", courses))
app_builder.add_handler(CommandHandler("learn", learn))
app_builder.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

await app_builder.initialize()
await app_builder.start()
await app_builder.updater.start_polling()
await app_builder.idle()

Start the bot in a background thread

threading.Thread(target=lambda: import asyncio; asyncio.run(run_bot())).start()

Main entry point for Render to run Flask

if name == "main": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

