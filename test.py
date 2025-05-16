from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
api_id = 1040477
api_hash = "ba3c1b7bbd8de520d2adb0e1187f5622"

app = Client("search_bot", api_id=api_id, api_hash=api_hash)
CHANNEL_ID = -1002664680052

@app.on_message(filters.command("search") & filters.private)
async def search_messages(client: Client, message: Message):
    try:
        # Extract the search keyword from the command
        keyword = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if not keyword:
            await message.reply("Please provide a keyword to search for.")
            return

        # Search for messages in the specified channel that contain the keyword
        async for msg in app.search_messages(CHANNEL_ID, query=keyword, limit=5):
            # Send each matching message to the user
            await message.reply(f"Found: {msg.text or '[No text content]'}", quote=True)

        # Inform the user if no messages were found
        if not keyword:
            await message.reply("No matching messages found.")

    except FloodWait as e:
        # Handle rate limiting
        await asyncio.sleep(e.x)

@bot.message_handler(commands=['getthisid'])
async def send_chat_id(message):
    chat_id = message.chat.id
    await bot.reply_to(message, f'Chat ID: {chat_id}')

if __name__ == "__main__":
    app.run()
