import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from koyeb_api import KoyebAPI

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

# Koyeb API token
KOYEB_API_TOKEN = os.environ['KOYEB_API_TOKEN']

# Render webhook URL
RENDER_WEBHOOK_URL = os.environ['RENDER_WEBHOOK_URL']

class KoyebBot:
    def __init__(self, token, koyeb_api):
        self.token = token
        self.koyeb_api = koyeb_api
        self.updater = Updater(token, use_context=True)
        self.app_id = None

        # Command handlers
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler('start', self.start))
        self.dp.add_handler(CommandHandler('help', self.help))
        self.dp.add_handler(CommandHandler('set_app_id', self.set_app_id))
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
        self.dp.add_handler(CommandHandler('status', self.status))

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to Koyeb Bot!')

    def help(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Available commands: /set_app_id, /create_app, /deploy, /redeploy, /logs, /env_vars, /set_env_var, /get_env_var, /delete_env_var, /list_apps, /get_app, /delete_app, /status')

    def set_app_id(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Enter your app ID:')
        def set_app_id_callback(update, context):
            self.app_id = update.message.text
            context.bot.send_message(chat_id=update.effective_chat.id, text='App ID set successfully!')
        self.dp.add_handler(MessageHandler(Filters.text, set_app_id_callback))

    def create_app(self, update, context):
        app_name = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app name:').result().text
        self.koyeb_api.create_app(app_name)
        context.bot.send_message(chat_id=update.effective_chat.id, text='App created successfully!')

    def deploy(self, update, context):
        if self.app_id:
            self.koyeb_api.deploy(self.app_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text='App deployed successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must set an app ID.')

    def redeploy(self, update, context):
        if self.app_id:
            self.koyeb_api.redeploy(self.app_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text='App redeploys successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must set an app ID.')

    def logs(self, update, context):
        if self.app_id:
            logs = self.koyeb_api.get_logs(self.app_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text=logs)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must set an app ID.')

    def env_vars(self, update, context):
        if self.app_id:
            env_vars = self.koyeb_api.get_env_vars(self.app_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text=env_vars)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must set an app ID.')

    def set_env_var(self, update, context):
        if self.app_id:
            key = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter key:').result().text
            value = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter value:').result().text
            self.koyeb_api.set_env_var(self.app_id, key, value)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Environment variable set successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must set an app ID.')

    def get_env_var(self, update, context):
        if self.app_id:
            key = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter key:').result().text
            value = self.koyeb_api.get_env_var(self.app_id, key)
            context.bot.send_message(chat_id=update.effective_chat.id, text=value)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must set an app ID.')

    def delete_env_var(self, update, context):
        if self.app_id:
            key = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter key:').result().text
            self.koyeb_api.delete_env_var(self.app_id, key)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Environment variable deleted successfully!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='You must set an app ID.')

    def list_apps(self, update, context):
        apps = self.koyeb_api.list_apps()
        context.bot.send_message(chat_id=update.effective_chat.id, text=apps)

    def get_app(self, update, context):
        app_id = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app ID:').result().text
        app = self.koyeb_api.get_app(app_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text=app)

    def delete_app(self, update, context):
        app_id = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter app ID:').result().text
        self.koyeb_api.delete_app(app_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text='App deleted successfully!')

    def status(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='App ID: ' + str(self.app_id))

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
    koyeb_api.login(KOYEB_API_TOKEN)

if __name__ == '__main__':
    main()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
