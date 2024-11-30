from flask import Flask, request, jsonify
from bot import bot
from koyeb_api import KoyebAPI

app = Flask(__name__)

# Webhook configuration
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    bot.process_update(update)
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
