from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")  # Optional fallback

last_alert = None  # Stores the last TradingView alert

def send_to_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print("Telegram response:", response.status_code, response.text)

@app.route("/", methods=["POST"])
def webhook():
    global last_alert
    try:
        data = request.get_json(force=True)
        print("Received TradingView Webhook:", data)

        if data:
            msg = f"📈 *TradingView Alert*\n\nEvent: {data.get('event')}\nTicker: {data.get('ticker')}\nPrice: {data.get('price')}\nTime: {data.get('time')}"
            last_alert = msg  # Store the latest alert
            send_to_telegram(CHAT_ID, msg)
            return "OK", 200
        return "No data", 400
    except Exception as e:
        print("Webhook error:", str(e))
        return "Bad Request", 400

@app.route("/bot", methods=["POST"])
def telegram_bot():
    global last_alert
    try:
        data = request.get_json(force=True)
        print("Bot received:", data)

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "").lower()

            if text == "/start":
                send_to_telegram(chat_id, "👋 Hello! I'm your TradingView alert bot. Type /help to see what I can do.")
            elif text == "/help":
                send_to_telegram(chat_id, "🛠 *Available Commands:*\n/start - Welcome message\n/status - Bot status\n/lastalert - Last received TradingView alert\n/help - Show this list")
            elif text == "/status":
                send_to_telegram(chat_id, "✅ I'm online and listening for TradingView alerts.")
            elif text == "/lastalert":
                if last_alert:
                    send_to_telegram(chat_id, f"📬 *Last Alert:*\n{last_alert}")
                else:
                    send_to_telegram(chat_id, "No alerts received yet.")
            else:
                send_to_telegram(chat_id, "❓ Unknown command. Type /help to see available options.")

        return "OK", 200
    except Exception as e:
        print("Bot error:", str(e))
        return "Bad Request", 400
