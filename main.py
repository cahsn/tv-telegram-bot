from flask import Flask, request
import requests

app = Flask(__name__)

# Telegram credentials
BOT_TOKEN = "8195018136:AAHxRl4glwZG6X_uEh9Z356-982GeOuJjm4"
CHAT_ID = "1662274091"

# Keep last alert
last_alert = None

def send_to_telegram(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = requests.post(url, json=payload)
    print("Telegram response:", response.status_code, response.text)

def send_trade_alert_with_buttons(event, ticker, price, time):
    global last_alert
    message = f"📈 *TradingView Alert*\n\n*Ticker:* `{ticker}`\n*Price:* {price}\n*Time:* {time}"
    last_alert = message  # Save for /lastalert
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Confirm Trade", "callback_data": "confirm"},
            {"text": "❌ Cancel", "callback_data": "cancel"}
        ]]
    }
    send_to_telegram(message, reply_markup=keyboard)

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("Received Webhook:", data)

        # Handle bot commands
        if "message" in data and "text" in data["message"]:
            text = data["message"]["text"]
            if text == "/start":
                send_to_telegram("👋 Hello! I'm ready to trade.")
            elif text == "/lastalert":
                send_to_telegram(last_alert if last_alert else "No alerts received yet.")
            return "OK", 200

        # Handle TradingView alert
        if data.get("event"):
            send_trade_alert_with_buttons(
                data.get("event"),
                data.get("ticker"),
                data.get("price"),
                data.get("time")
            )
            return "OK", 200

        return "No data", 400

    except Exception as e:
        print("Webhook error:", str(e))
        return "Bad Request", 400

@app.route("/callback", methods=["POST"])
def callback():
    try:
        data = request.get_json()
        callback_query = data.get("callback_query", {})
        user_choice = callback_query.get("data")
        user_id = callback_query.get("from", {}).get("id")
        message_id = callback_query.get("message", {}).get("message_id")

        # Acknowledge button press
        ack_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
        requests.post(ack_url, json={"callback_query_id": callback_query["id"]})

        # Respond to choice
        response_text = "✅ Trade Confirmed!" if user_choice == "confirm" else "❌ Trade Canceled."
        edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload = {
            "chat_id": user_id,
            "message_id": message_id,
            "text": response_text
        }
        requests.post(edit_url, json=payload)
        return "OK", 200

    except Exception as e:
        print("Callback error:", str(e))
        return "Bad Request", 400
