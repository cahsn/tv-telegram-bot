from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    if data:
        msg = f"📈 *TradingView Alert*\n\nEvent: {data.get('event')}\nTicker: {data.get('ticker')}\nPrice: {data.get('price')}\nTime: {data.get('time')}"
        send_to_telegram(msg)
        return "OK", 200
    return "No data", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
