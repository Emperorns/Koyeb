import logging
import psycopg2
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgres://koyeb-adm:khFat50DlXGj@ep-purple-cloud-a28j7t3o.eu-central-1.pg.koyeb.app/koyebdb"
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cursor = conn.cursor()

# Create necessary tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    api_key TEXT NOT NULL
)
""")
conn.commit()


# Start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Welcome to the Koyeb Manager Bot!\n\n"
        "Manage your Koyeb apps directly from Telegram.\n"
        "Use /login to link your account, /createapp to deploy a new app, or /redeploy to redeploy an app."
    )


# Login command
async def login(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Please send your Koyeb API Key. Your account will be linked to this bot."
    )
    context.user_data["awaiting_api_key"] = True


# Handle API key input
async def handle_api_key(update: Update, context: CallbackContext) -> None:
    if context.user_data.get("awaiting_api_key"):
        api_key = update.message.text
        telegram_id = update.message.from_user.id

        # Save API key to database
        cursor.execute(
            "INSERT INTO accounts (telegram_id, api_key) VALUES (%s, %s) ON CONFLICT (telegram_id) DO UPDATE SET api_key = EXCLUDED.api_key",
            (telegram_id, api_key),
        )
        conn.commit()

        await update.message.reply_text("Your account has been linked successfully!")
        context.user_data["awaiting_api_key"] = False


# Redeploy an app
async def redeploy(update: Update, context: CallbackContext) -> None:
    telegram_id = update.message.from_user.id
    cursor.execute("SELECT api_key FROM accounts WHERE telegram_id=%s", (telegram_id,))
    account = cursor.fetchone()

    if account:
        api_key = account[0]
        await update.message.reply_text("Please provide the Service ID of the app to redeploy.")
        context.user_data["awaiting_service_redeploy"] = api_key
    else:
        await update.message.reply_text("No account linked. Use /login to link your account.")


async def handle_redeploy(update: Update, context: CallbackContext) -> None:
    if not context.user_data.get("awaiting_service_redeploy"):
        return

    api_key = context.user_data["awaiting_service_redeploy"]
    service_id = update.message.text

    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(
        f"https://app.koyeb.com/api/v1/services/{service_id}/deployments", headers=headers
    )

    if response.status_code == 201:
        await update.message.reply_text("App redeployed successfully!")
    else:
        await update.message.reply_text("Failed to redeploy app. Please check the Service ID.")

    context.user_data["awaiting_service_redeploy"] = None


# Create a new app
async def create_app(update: Update, context: CallbackContext) -> None:
    telegram_id = update.message.from_user.id
    cursor.execute("SELECT api_key FROM accounts WHERE telegram_id=%s", (telegram_id,))
    account = cursor.fetchone()

    if account:
        api_key = account[0]
        await update.message.reply_text(
            "Please provide the app name and GitHub repository URL (in format: `app_name,repo_url`)."
        )
        context.user_data["awaiting_app_creation"] = api_key
    else:
        await update.message.reply_text("No account linked. Use /login to link your account.")


async def handle_app_creation(update: Update, context: CallbackContext) -> None:
    if not context.user_data.get("awaiting_app_creation"):
        return

    api_key = context.user_data["awaiting_app_creation"]
    try:
        app_name, repo_url = update.message.text.split(",")
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "name": app_name.strip(),
            "git": {
                "repository": repo_url.strip(),
                "branch": "main",
                "build_command": "python bot.py",
                "run_command": "python bot.py",
            },
        }

        response = requests.post("https://app.koyeb.com/api/v1/services", json=data, headers=headers)

        if response.status_code == 201:
            await update.message.reply_text(f"App `{app_name}` created successfully!")
        else:
            await update.message.reply_text("Failed to create app. Check the input format.")
    except ValueError:
        await update.message.reply_text("Invalid format. Use: `app_name,repo_url`")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

    context.user_data["awaiting_app_creation"] = None


# Main function to run the bot
async def main():
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("redeploy", redeploy))
    app.add_handler(CommandHandler("createapp", create_app))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_key))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_redeploy))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_app_creation))

    # Webhook configuration
    WEBHOOK_URL = "https://your-koyeb-app-url.com/webhook"
    await app.bot.set_webhook(WEBHOOK_URL)

    print("Bot is running with webhook!")
    await app.start()
    await app.updater.idle()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
