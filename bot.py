import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import Update
from koyeb_api import KoyebAPI
from flask import Flask, request, jsonify

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

# Render webhook URL
RENDER_WEBHOOK_URL = os.environ['RENDER_WEBHOOK_URL']

LOGIN = range(1)
SET_APP_ID = range(1)

class KoyebBot:
    def __init__(self, token, koyeb_api):
        self.token = token
        self.koyeb_api = koyeb_api
        self.updater = Updater(token, use_context=True)
        self.logged_in = False
        self.app_id = None

        # Command handlers
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler('start', self.start))
        self.dp.add_handler(CommandHandler('help', self.help))
        self.dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('login', self.login)],
            states={LOGIN: [MessageHandler(Filters.text, self.login_callback)]},
            fallbacks=[]
        ))
        self.dp.add_handler(CommandHandler('logout', self.logout))
        self.dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('set_app_id', self.set_app_id)],
            states={SET_APP_ID: [MessageHandler(Filters.text, self.set_app_id_callback)]},
            fallbacks=[]
        ))
        self.dp.add_handler(CommandHandler('create_app', self.create_app))
        self.dp.add_handler(CommandHandler('deploy', self.deploy))
        self.dp.add_handler(CommandHandler('redeploy', self.redeploy))
        self.dp.add_handler(CommandHandler('logs', self.logs))
        self.dp.add_handler(CommandHandler('env_vars', self.env_vars))
        self.dp.add_handler(CommandHandler('set_env_var', self.set_env_var))
        self.dp.add_handler(CommandHandler('get_env_var', self.get_env_var))
        self.dp.add_handler(CommandHandler('delete_env_var', self.delete_env_var))
        self.dp.add_handler(CommandHandler('list_apps', self.list_apps))
        self.dp.add_handler(CommandHandler('get_app', self.get_app))
        self.dp.add_handler(CommandHandler('delete_app', self.delete_app))

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to Koyeb Bot!')

    def help(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Available commands: /login, /logout, /set_app_id, /create_app, /deploy, /redeploy, /logs, /env_vars, /set_env_var, /get_env_var, /delete_env_var, /list_apps, /get_app, /delete_app')

    def login(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Enter your Koyeb API key:')
        return LOGIN

    def login_callback(self, update, context):
        api_key = update.message.text
        try:
            self.koyeb_api.login(api_key)
            self.logged_in = True
            context.bot.send_message(chat_id=update.effective_chat.id, text='Logged in successfully!')
            print(f'Logged in successfully! {api_key}')
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Login failed: {str(e)}')
            print(f'Login failed: {str(e)}')
        return ConversationHandler.END

    def logout(self, update, context):
        if self.logged_in:
            self.koyeb_api.logout()
            self.logged_in = False
            context.bot.send_message(chat_id=update.effective_chat.id, text='Logged out successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You are not logged in.')

    def set_app_id(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Enter your app ID:')
        return SET_APP_ID

    def set_app_id_callback(self, update, context):
        self.app_id = update.message.text
        context.bot.send_message(chat_id=update.effective_chat.id, text='App ID set successfully!')
        return ConversationHandler.END

    def create_app(self, update, context):
        if self.logged_in:
            app_name = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app name:').result()
            self.koyeb_api.create_app(app_name.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text='App created successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in.')

    def deploy(self, update, context):
        if self.logged_in and self.app_id:
            self.koyeb_api.deploy(self.app_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text='App deployed successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in and have an app ID set.')

    def redeploy(self, update, context):
        if self.logged_in and self.app_id:
            self.koyeb_api.redeploy(self.app_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text='App redeploys successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in and have an app ID set.')

    def logs(self, update, context):
        if self.logged_in and self.app_id:
            logs = self.koyeb_api.get_logs(self.app_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text=logs)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in and have an app ID set.')

    def env_vars(self, update, context):
        if self.logged_in and self.app_id:
            env_vars = self.koyeb_api.get_env_vars(self.app_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text=env_vars)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in and have an app ID set.')

    def set_env_var(self, update, context):
        if self.logged_in and self.app_id:
            key = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter key:').result()
            value = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter value:').result()
            self.koyeb_api.set_env_var(self.app_id, key.text, value.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Environment variable set successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in and have an app ID set.')

    def get_env_var(self, update, context):
        if self.logged_in and self.app_id:
            key = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter key:').result()
            value = self.koyeb_api.get_env_var(self.app_id, key.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text=value)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in and have an app ID set.')

    def delete_env_var(self, update, context):
        if self.logged_in and self.app_id:
            key = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter key:').result()
            self.koyeb_api.delete_env_var(self.app_id, key.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Environment variable deleted successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in and have an app ID set.')

    def list_apps(self, update, context):
        if self.logged_in:
            apps = self.koyeb_api.list_apps()
            context.bot.send_message(chat_id=update.effective_chat.id, text=apps)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in.')

    def get_app(self, update, context):
        if self.logged_in:
            app_id = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app ID:').result()
            app = self.koyeb_api.get_app(app_id.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text=app)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in.')

    def delete_app(self, update, context):
        if self.logged_in:
            app_id = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app ID:').result()
            self.koyeb_api.delete_app(app_id.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text='App deleted successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must be logged in.')

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_webhook():
    update = request.get_json()
    bot = KoyebBot(TELEGRAM_BOT_TOKEN, KoyebAPI())
    bot.updater.dispatcher.process_update(Update.de_json(update, bot.updater.bot))
    return 'OK', 200

def main():
    koyeb_api = KoyebAPI()
    bot = KoyebBot(TELEGRAM_BOT_TOKEN, koyeb_api)

if __name__ == '__main__':
    main()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
