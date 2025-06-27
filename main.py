from flask import Flask, request
import requests

app = Flask(__name__)

# Your Telegram bot token and chat ID
BOT_TOKEN = "8195018136:AAHxRl4glwZG6X_uEh9Z356-982GeOuJjm4"
CHAT_ID = "1662274091"

def send_trade_alert_with_buttons(event, ticker, price, time):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = f"📈 *TradingView Alert*\n\n*Ticker:* `{ticker}`\n*Price:* {price}\n*Time:* {time}"
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Confirm Trade", "callback_data": "confirm"},
            {"text": "❌ Cancel", "callback_data": "cancel"}
        ]]
    }
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }
    response = requests.post(url, json=payload)
    print("Telegram response:", response.status_code, response.text)

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("Received Webhook:", data)

        if data:
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

        # Acknowledge the button press
        ack_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
        requests.post(ack_url, json={"callback_query_id": callback_query["id"]})

        # Respond based on the button pressed
        if user_choice == "confirm":
            text = "✅ Trade Confirmed!"
        else:
            text = "❌ Trade Canceled."

        edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload = {
            "chat_id": user_id,
            "message_id": message_id,
            "text": text
        }
        requests.post(edit_url, json=payload)
        return "OK", 200

    except Exception
