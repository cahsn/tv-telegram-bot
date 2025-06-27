from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Store last alert globally
last_alert = "No alerts yet."

def send_to_telegram(message, chat_id=CHAT_ID):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print("Telegram response:", response.status_code, response.text)

# === TradingView Webhook ===
@app.route("/", methods=["POST"])
def webhook():
    global last_alert
    try:
        data = request.get_json(force=True)
        print("Received Webhook:", data)

        if data:
            msg = f"📈 *TradingView Alert*\n\nEvent: {data.get('event')}\nTicker: {data.get('ticker')}\nPrice: {data.get('price')}\nTime: {data.get('time')}"
            last_alert = msg
            send_to_telegram(msg)
            return "OK", 200
        return "No data", 400
    except Exception as e:
        print("Webhook error:", str(e))
        return "Bad Request", 400

# === Telegram Command Handler ===
@app.route("/bot", methods=["POST"])
def telegram_bot():
    global last_alert
    data = request.get_json()
    print("Bot received:", data)

    message = data.get("message", {})
    text = message.get("text", "").lower()
    chat_id = message.get("chat", {}).get("id")

    if text == "/start":
        send_to_telegram("👋 Hello! I'm your TradingView alert bot. Send /lastalert to view the most recent alert.", chat_id)
    elif text == "/lastalert":
        send_to_telegram(last_alert, chat_id)
    else:
        send_to_telegram("❓ Unknown command. Use /start or /lastalert.", chat_id)

    return "OK", 200
