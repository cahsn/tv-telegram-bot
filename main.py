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

# === Webhook from TradingView ===
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)  # Force parse even without correct Content-Type
        print("Received Webhook:", data)

        if data:
            msg = f"📈 *TradingView Alert*\n\nEvent: {data.get('event')}\nTicker: {data.get('ticker')}\nPrice: {data.get('price')}\nTime: {data.get('time')}"
            send_to_telegram(msg)
            return "OK", 200
        return "No data", 400

    except Exception as e:
        print("Webhook error:", str(e))
        return "Bad Request", 400

# === Bot Command Handler ===
@app.route("/bot", methods=["POST"])
def telegram_bot():
    try:
        data = request.get_json(force=True)
        print("Bot received:", data)

        if "message" in data:
            chat_id = str(data["message"]["chat"]["id"])
            text = data["message"].get("text", "")

            if chat_id != CHAT_ID:
                return "Unauthorized", 403

            if text == "/start":
                send_to_telegram("👋 Hello! I'm your trading bot.")
            elif text == "/status":
                send_to_telegram("✅ Bot is running and connected to TradingView.")
            elif text == "/latest":
                send_to_telegram("📈 Latest alert info coming soon.")
            else:
                send_to_telegram("❓ Unknown command. Try /start or /status")

        return "OK", 200

    except Exception as e:
        print("Bot handler error:", str(e))
        return "Error", 400
