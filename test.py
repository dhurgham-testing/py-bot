from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
api_id = 1040477
api_hash = "ba3c1b7bbd8de520d2adb0e1187f5622"

app = Client("search_bot", api_id=api_id, api_hash=api_hash)
CHANNEL_ID = -1002664680052  # your channel ID

@app.on_message(filters.command("search") & filters.private)
async def search_messages(client, message):
    try:
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            await message.reply("Please provide a keyword to search for.")
            return
        keyword = parts[1]

        found_any = False
        async for msg in app.search_messages(CHANNEL_ID, query=keyword, limit=5):
            found_any = True
            content = msg.text or msg.caption or "[No text content]"
            await message.reply(f"Found: {content}", quote=True)

        if not found_any:
            await message.reply("No matching messages found.")

    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command("getthisid"))
async def send_chat_id(client, message):
    chat_id = message.chat.id
    await message.reply(f"Chat ID: {chat_id}")

if __name__ == "__main__":
    app.run()
