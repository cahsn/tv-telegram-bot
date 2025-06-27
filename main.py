from flask import Flask, request
import os, requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID   = os.getenv("CHAT_ID")

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json or {}
    msg = (
        f"📈 *TradingView Alert*\n\n"
        f"*Event:* {data.get('event')}\n"
        f"*Ticker:* {data.get('ticker')}\n"
        f"*Price:* {data.get('price')}\n"
        f"*Time:* {data.get('time')}"
    )
    send_to_telegram(msg)
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
