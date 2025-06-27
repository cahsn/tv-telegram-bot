from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print("Telegram response:", response.status_code, response.text)

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("Received Webhook:", data)

        if data:
            msg = f"📈 *TradingView Alert*\n\nEvent: {data.get('event')}\nTicker: {data.get('ticker')}\nPrice: {data.get('price')}\nTime: {data.get('time')}"
            send_to_telegram(msg)
            return "OK", 200
        return "No data", 400

    except Exception as e:
        pri
