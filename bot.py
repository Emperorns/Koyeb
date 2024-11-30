import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from koyeb_api import KoyebAPI
from models import User

logging.basicConfig(level=logging.INFO)

class KoyebBot:
    def __init__(self, token, koyeb_api):
        self.token = token
        self.koyeb_api = koyeb_api
        self.updater = Updater(token, use_context=True)

        # Command handlers
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler('start', self.start))
        self.dp.add_handler(CommandHandler('help', self.help))
        self.dp.add_handler(CommandHandler('login', self.login))
        self.dp.add_handler(CommandHandler('logout', self.logout))
        self.dp.add_handler(CommandHandler('create_app', self.create_app))
        self.dp.add_handler(CommandHandler('redeploy', self.redeploy))
        self.dp.add_handler(CommandHandler('logs', self.logs))
        self.dp.add_handler(CommandHandler('env_vars', self.env_vars))

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to Koyeb Bot!')

    def help(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Available commands: /login, /logout, /create_app, /redeploy, /logs, /env_vars')

    def login(self, update, context):
        # Login logic using Koyeb API
        api_key = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter your Koyeb API key:').result()
        self.koyeb_api.login(api_key.text)

    def logout(self, update, context):
        # Logout logic using Koyeb API
        self.koyeb_api.logout()

    def create_app(self, update, context):
        # Create app logic using Koyeb API
        app_name = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app name:').result()
        self.koyeb_api.create_app(app_name.text)

    def redeploy(self, update, context):
        # Redeploy logic using Koyeb API
        app_id = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app ID:').result()
        self.koyeb_api.redeploy(app_id.text)

    def logs(self, update, context):
        # Logs logic using Koyeb API
        app_id = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app ID:').result()
        logs = self.koyeb_api.get_logs(app_id.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text=logs)

    def env_vars(self, update, context):
        # Env vars logic using Koyeb API
        app_id = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app ID:').result()
        env_vars = self.koyeb_api.get_env_vars(app_id.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text=env_vars)

def main():
    koyeb_api = KoyebAPI()
    bot = KoyebBot('YOUR_TELEGRAM_BOT_TOKEN', koyeb_api)
    bot.updater.start_webhook(listen='127.0.0.1', port=5000, url_path='YOUR_TELEGRAM_BOT_TOKEN', webhook_url='YOUR_RENDER_WEBHOOK_URL')
    bot.updater.idle()

if __name__ == '__main__':
    main()
