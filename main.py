from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Telegram bot token and chat ID
BOT_TOKEN = "8195018136:AAHxRl4glwZG6X_uEh9Z356-982GeOuJjm4"
CHAT_ID = "1662274091"

# Helper to clean up TradingView ticker format
def simplify_ticker(raw_ticker):
    if not raw_ticker:
        return "Unknown"
    base = raw_ticker.split("_")[0]
    quote_tokens = ["WETH", "ETH", "USDC", "USDT", "BTC"]
    for quote in quote_tokens:
        if base.endswith(quote) and base != quote:
            base_token = base[:-len(quote)]
            return f"{base_token}/{quote}"
    return base

# Send alert message with confirm/cancel buttons
def send_trade_alert_with_buttons(event, ticker, price, time):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = f"\ud83d\udcc8 *TradingView Alert*\n\n*Ticker:* `{ticker}`\n*Price:* {price}\n*Time:* {time}"
    keyboard = {
        "inline_keyboard": [[
            {"text": "\u2705 Confirm Trade", "callback_data": f"confirm|{ticker}|{price}|{time}"},
            {"text": "\u274c Cancel", "callback_data": "cancel"}
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
            simplified = simplify_ticker(data.get("ticker"))
            send_trade_alert_with_buttons(
                data.get("event"),
                simplified,
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

        if user_choice.startswith("confirm|"):
            _, ticker, price, time = user_choice.split("|")
            text = f"\u2705 Trade Confirmed for {ticker} at {price} at {time}"
        else:
            text = "\u274c Trade Canceled."

        edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload = {
            "chat_id": user_id,
            "message_id": message_id,
            "text": text
        }
        requests.post(edit_url, json=payload)
        return "OK", 200

    except Exception as e:
        print("Callback error:", str(e))
        return "Bad Request", 400

# ✅ Required for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
