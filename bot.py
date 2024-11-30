import os
import logging
import psycopg2
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.ext import Dispatcher

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Connect to the PostgreSQL database
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Ensure the necessary tables exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id BIGINT PRIMARY KEY,
    koyeb_api_key TEXT,
    koyeb_email TEXT,
    koyeb_password TEXT
);
""")
conn.commit()

# Flask app for webhook
app = Flask(__name__)

# Create Application instance
application = Application.builder().token(BOT_TOKEN).build()

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    telegram_id = user.id
    cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = %s", (telegram_id,))
    if cursor.fetchone():
        await update.message.reply_text("Welcome back! You're already registered.")
    else:
        await update.message.reply_text("Welcome! Please register using /register.")
        cursor.execute("INSERT INTO users (telegram_id) VALUES (%s) ON CONFLICT DO NOTHING", (telegram_id,))
        conn.commit()

# Command: Register Koyeb Account
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: /register <koyeb_api_key> <koyeb_email> <koyeb_password>"
        )
        return

    telegram_id = update.effective_user.id
    koyeb_api_key = context.args[0]
    koyeb_email = context.args[1]
    koyeb_password = context.args[2]

    cursor.execute(
        """
        UPDATE users 
        SET koyeb_api_key = %s, koyeb_email = %s, koyeb_password = %s 
        WHERE telegram_id = %s
        """,
        (koyeb_api_key, koyeb_email, koyeb_password, telegram_id),
    )
    conn.commit()
    await update.message.reply_text("Your Koyeb account has been registered!")

# Command: Create a New Koyeb Account
async def create_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /create_account <koyeb_email> <koyeb_password>"
        )
        return

    koyeb_email = context.args[0]
    koyeb_password = context.args[1]
    # Simulate account creation
    # Replace with actual API call to Koyeb if available
    await update.message.reply_text(
        f"Account created successfully for {koyeb_email}!"
    )

# Command: Show Koyeb Info
async def koyeb_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    cursor.execute(
        "SELECT koyeb_api_key, koyeb_email FROM users WHERE telegram_id = %s", (telegram_id,)
    )
    result = cursor.fetchone()
    if result:
        koyeb_api_key, koyeb_email = result
        await update.message.reply_text(
            f"Koyeb API Key: {koyeb_api_key}\nKoyeb Email: {koyeb_email}"
        )
    else:
        await update.message.reply_text("You are not registered. Use /register to register.")

# Command: Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start - Start the bot\n"
        "/register <api_key> <email> <password> - Register your Koyeb account\n"
        "/create_account <email> <password> - Create a new Koyeb account\n"
        "/koyeb_info - Show your Koyeb account info\n"
        "/help - Show this help message"
    )

# Flask route to receive webhook requests
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.update_queue.put(update)  # Push update to the dispatcher
    return "OK", 200

# Dispatcher for handling updates
dispatcher = Dispatcher(application.bot, application.update_queue)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("register", register))
dispatcher.add_handler(CommandHandler("create_account", create_account))
dispatcher.add_handler(CommandHandler("koyeb_info", koyeb_info))
dispatcher.add_handler(CommandHandler("help", help_command))

# Start the Flask app
if __name__ == '__main__':
    # Set the webhook URL
    application.bot.set_webhook(WEBHOOK_URL)

    # Start Flask app to listen for updates
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
