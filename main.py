from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Get Telegram credentials from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram message sender
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Failed to send to Telegram:", e)

# Webhook route for TradingView
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("Received data:", data)

        if data:
            msg = f"📈 *TradingView Alert*\n\nEvent: {data.get('event')}\nTicker: {data.get('ticker')}\nPrice: {data.get('price')}\nTime: {data.get('time')}"
            send_to_telegram(msg)
            return "OK", 200  # Respond quickly
        else:
            return "Invalid data", 400

    except Exception as e:
        print("Webhook error:", str(e))
        return "Internal Server Error", 500

# Optional: health check route
@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200
