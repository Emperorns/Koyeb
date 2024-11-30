from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from koyeb_client import KoyebClient
import os

class KoyebTelegramBot:
    def __init__(self, token, koyeb_client):
        self.token = token
        self.koyeb_client = koyeb_client
        self.apps = {}

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Koyeb Telegram Bot!")

    def create_app(self, update, context):
        if len(context.args) != 2:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /create_app <name> <docker_image>")
            return
        name, docker_image = context.args
        app = self.koyeb_client.create_app(name, docker_image)
        self.apps[app["id"]] = app
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"App created: {app['name']}")

    def deploy_app(self, update, context):
        if len(context.args) != 2:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /deploy_app <app_id> <docker_image>")
            return
        app_id, docker_image = context.args
        deployment = self.koyeb_client.deploy_app(app_id, docker_image)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"App deployed: {deployment['app']['name']}")

    def delete_app(self, update, context):
        if len(context.args) != 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /delete_app <app_id>")
            return
        app_id = context.args[0]
        self.koyeb_client.delete_app(app_id)
        del self.apps[app_id]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"App deleted: {app_id}")

    def select_app(self, update, context):
        if len(context.args) != 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /select_app <app_id>")
            return
        app_id = context.args[0]
        app = self.apps.get(app_id)
        if app:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Selected app: {app['name']}")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"App not found: {app_id}")

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    koyeb_client = KoyebClient()
    bot = KoyebTelegramBot(token, koyeb_client)

    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", bot.start))
    dp.add_handler(CommandHandler("create_app", bot.create_app))
    dp.add_handler(CommandHandler("deploy_app", bot.deploy_app))
    dp.add_handler(CommandHandler("delete_app", bot.delete_app))
    dp.add_handler(CommandHandler("select_app", bot.select_app))

    # Handle incoming updates from Telegram
    dp.add_handler(MessageHandler(Filters.text, bot.select_app))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
