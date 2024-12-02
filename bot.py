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
        self.dp.add_handler(CommandHandler('list_apps', self.list_apps))
        self.dp.add_handler(CommandHandler('get_app', self.get_app))
        self.dp.add_handler(CommandHandler('delete_app', self.delete_app))
        self.dp.add_handler(CommandHandler('get_account_info', self.get_account_info))
        self.dp.add_handler(CommandHandler('update_account_info', self.update_account_info))
        self.dp.add_handler(CommandHandler('get_invoice', self.get_invoice))
        self.dp.add_handler(CommandHandler('get_invoices', self.get_invoices))

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to Koyeb Bot!')

    def help(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Available commands: /list_apps, /get_app, /delete_app, /get_account_info, /update_account_info, /get_invoice, /get_invoices')

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

    def get_account_info(self, update, context):
        account_info = self.koyeb_api.get_account_info()
        context.bot.send_message(chat_id=update.effective_chat.id, text=account_info)

    def update_account_info(self, update, context):
        data = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter new account info (JSON):').result().text
        self.koyeb_api.update_account_info(data)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Account info updated successfully!')

    def get_invoice(self, update, context):
        invoice_id = context.bot.send_message(chat_id=update.effective_chat.id, text='Enter invoice ID:').result().text
        invoice = self.koyeb_api.get_invoice(invoice_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text=invoice)

    def get_invoices(self, update, context):
        invoices = self.koyeb_api.get_invoices()
        context.bot.send_message(chat_id=update.effective_chat.id, text=invoices)

def main():
    koyeb_api = KoyebAPI()
    koyeb_api.login(KOYEB_API_TOKEN)
    bot = KoyebBot(TELEGRAM_BOT_TOKEN, koyeb_api)
    bot.updater.start_polling()
    bot.updater.idle()

if __name__ == '__main__':
    main()
