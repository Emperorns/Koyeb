import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import Update
from koyeb_api import KoyebAPI
from models import User
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

        # Command handlers
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler('start', self.start))
        self.dp.add_handler(CommandHandler('help', self.help))
        self.dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('login', self.login)],
            states={LOGIN: [MessageHandler(Filters.text, self.login_callback)]},
            fallbacks=[]
        ))
        self.dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler('set_app_id', self.set_app_id)],
            states={SET_APP_ID: [MessageHandler(Filters.text, self.set_app_id_callback)]},
            fallbacks=[]
        ))

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to Koyeb Bot!')

    def help(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Available commands: /login, /set_app_id')

    def login(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Enter your Koyeb API key:')
        return LOGIN

    def login_callback(self, update, context):
        api_key = update.message.text
        self.koyeb_api.login(api_key)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Logged in successfully!')
        return ConversationHandler.END

    def set_app_id(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Enter your app ID:')
        return SET_APP_ID

    def set_app_id_callback(self, update, context):
        app_id = update.message.text
        self.koyeb_api.set_app_id(app_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text='App ID set successfully!')
        return ConversationHandler.END

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
