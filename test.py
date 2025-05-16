
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
api_id = 1040477
api_hash = "ba3c1b7bbd8de520d2adb0e1187f5622"

app = Client("search_bot", api_id=api_id, api_hash=api_hash)
CHANNEL_ID = -1002664680052
ALLOWED_USERS = [959599690, 996193663]

@app.on_message(filters.private & filters.text)
async def search_messages(client: Client, message: Message):
    if message.from_user.id not in ALLOWED_USERS:
        return

    if not message.text.startswith("دورلي "):
        return

    try:
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            await message.reply("اكتب الكلمة بعد 'دورلي'")
            return

        keyword = parts[1]
        found_any = False

        async for msg in app.search_messages(CHANNEL_ID, query=keyword, limit=5):
            found_any = True
            await app.forward_messages(
                chat_id=message.chat.id,
                from_chat_id=CHANNEL_ID,
                message_ids=msg.id
            )

        if not found_any:
            await message.reply("ماكو نتائج.")

    except FloodWait as e:
        await asyncio.sleep(e.x)

@app.on_message(filters.command("getthisid") & filters.private)
async def send_chat_id(client: Client, message: Message):
    chat_id = message.chat.id
    await message.reply(f"Chat ID: {chat_id}")

if __name__ == "__main__":
    app.run()
