import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from flask import Flask
from threading import Thread

# ================= ENV VARIABLES ================= #

def get_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing environment variable: {name}")
    return value

API_ID = int(get_env("API_ID"))
API_HASH = get_env("API_HASH")
SOURCE_ID = int(get_env("SOURCE_ID"))
TARGET_ID = int(get_env("TARGET_ID"))

# ================= TELEGRAM CLIENT ================= #

client = TelegramClient("session", API_ID, API_HASH)

# ================= KEEP ALIVE SERVER ================= #

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Scalping Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================= TELEGRAM LISTENER ================= #

async def telegram_listener():
    await client.start()
    print("✅ Telegram Connected")

    @client.on(events.NewMessage(chats=SOURCE_ID))
    async def handler(event):
        try:
            if not event.message.text:
                return

            formatted = f"""
🕒 {event.message.date.strftime('%Y-%m-%d %H:%M:%S')}

{event.message.text}
"""

            await client.send_message(TARGET_ID, formatted)
            print("⚡ Signal Forwarded")

        except FloodWaitError as e:
            print(f"⏳ Flood wait: {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print("Error:", e)

    print("🚀 Listening in REAL-TIME...")
    await client.run_until_disconnected()

# ================= AUTO RECONNECT LOOP ================= #

async def main():
    while True:
        try:
            await telegram_listener()
        except Exception as e:
            print("🔁 Reconnecting due to error:", e)
            await asyncio.sleep(5)

# ================= START APP ================= #

if __name__ == "__main__":
    Thread(target=run_web).start()
    asyncio.run(main())
