import os
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import requests

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create tables if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id BIGINT PRIMARY KEY,
    active_account_id SERIAL
);
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT REFERENCES users(telegram_id),
    api_key TEXT,
    email TEXT,
    password TEXT
);
""")
conn.commit()

def start(update: Update, context: CallbackContext):
    """Welcome message and command instructions."""
    update.message.reply_text(
        "Welcome to the Koyeb Manager Bot! Use /login to link your account, /create to create a new account, or /help for more options."
    )

def login(update: Update, context: CallbackContext):
    """Start the login process."""
    update.message.reply_text(
        "Please enter your Koyeb credentials as: `API_KEY` or `email,password`",
        parse_mode="Markdown"
    )
    context.user_data['awaiting_credentials'] = True

def handle_credentials(update: Update, context: CallbackContext):
    """Handle the API key or email/password provided by the user."""
    if not context.user_data.get('awaiting_credentials'):
        return

    credentials = update.message.text.split(",")
    telegram_id = update.message.from_user.id

    if len(credentials) == 1:  # API Key
        api_key = credentials[0]
        cursor.execute("INSERT INTO accounts (telegram_id, api_key) VALUES (%s, %s)", (telegram_id, api_key))
    elif len(credentials) == 2:  # Email and password
        email, password = credentials
        cursor.execute("INSERT INTO accounts (telegram_id, email, password) VALUES (%s, %s, %s)", (telegram_id, email, password))
    else:
        update.message.reply_text("Invalid format. Please try again.")
        return

    conn.commit()
    context.user_data['awaiting_credentials'] = False
    update.message.reply_text("Account linked successfully! Use /services to manage your web apps.")

def create_account(update: Update, context: CallbackContext):
    """Create a new Koyeb account."""
    update.message.reply_text("Please provide your email and password as: `email,password`", parse_mode="Markdown")
    context.user_data['awaiting_creation'] = True

def handle_account_creation(update: Update, context: CallbackContext):
    """Handle account creation."""
    if not context.user_data.get('awaiting_creation'):
        return

    email, password = update.message.text.split(",")
    response = requests.post("https://app.koyeb.com/api/v1/accounts", json={"email": email, "password": password})

    if response.status_code == 201:
        update.message.reply_text("Account created successfully! Use /login to link it.")
    else:
        update.message.reply_text("Failed to create account. Please try again.")
    
    context.user_data['awaiting_creation'] = False

def help_command(update: Update, context: CallbackContext):
    """Display help."""
    update.message.reply_text("/login - Link an existing account\n/create - Create a new Koyeb account\n/services - Manage web apps")

def services(update: Update, context: CallbackContext):
    """List and manage Koyeb services."""
    telegram_id = update.message.from_user.id
    cursor.execute("SELECT api_key FROM accounts WHERE telegram_id=%s", (telegram_id,))
    account = cursor.fetchone()

    if account:
        api_key = account[0]
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://app.koyeb.com/api/v1/services", headers=headers)
        services = response.json()
        
        if services.get("services"):
            buttons = [
                [InlineKeyboardButton(s["name"], callback_data=f"service:{s['id']}")]
                for s in services["services"]
            ]
            update.message.reply_text("Select a service to manage:", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            update.message.reply_text("No services found.")
    else:
        update.message.reply_text("No linked account found. Use /login to link your account.")

def main():
    """Run the bot."""
    updater = Updater(os.getenv("BOT_TOKEN"))
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("create", create_account))
    dp.add_handler(CommandHandler("services", services))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_credentials))
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_account_creation))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
