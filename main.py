import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from twilio.rest import Client
import elevenlabs

# Set up API keys
TELEGRAM_BOT_TOKEN = "7961662822:AAHYmIZWt5B5JaKBfoybr4otOH7kDtJwA_8"
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
ELEVENLABS_VOICE_ID = "your_elevenlabs_voice_id"

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram Bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Twilio client
twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Function to convert text to speech and make a call
def call_user(phone_number, text):
    audio = elevenlabs.text_to_speech(api_key=ELEVENLABS_API_KEY, text=text, voice_id=ELEVENLABS_VOICE_ID)

    call = twilio_client.calls.create(
        twiml=f'<Response><Play>{audio}</Play></Response>',
        to=phone_number,
        from_=TWILIO_PHONE_NUMBER
    )
    return call.sid

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a number and a message to call.")

# Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    parts = text.split(" ", 1)

    if len(parts) == 2:
        phone_number, message = parts
        call_sid = call_user(phone_number, message)
        await update.message.reply_text(f"Calling {phone_number} with message: {message}\nCall SID: {call_sid}")
    else:
        await update.message.reply_text("Send message in this format:\n`+1234567890 Your message`")

# Set up command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook route
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)