import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
from mishkal import tashkeel



api_id = 1040477
api_hash = "ba3c1b7bbd8de520d2adb0e1187f5622"

app = Client("search_bot", api_id=api_id, api_hash=api_hash)
CHANNEL_ID = -1002664680052
ALLOWED_USERS = [959599690, 996193663]
tashkel = tashkeel
vocalizer =tashkel.TashkeelClass()


@app.on_message(filters.private & filters.text)
async def handle_commands(client: Client, message: Message):
    if message.from_user.id not in ALLOWED_USERS:
        return

    if message.from_user.id == 959599690 and message.chat.id == 996193663:
        harakat = vocalizer.tashkeel(message.text)
        if harakat != message.text:
            await app.edit_message_text(message.chat.id, message.id, harakat)

    text = message.text.strip()

    # ✅ أمر "دورلي"
    if text.startswith("دورلي "):
        try:
            parts = text.split(" ", 1)
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

    if text.startswith("/dl "):
        try:
            url = text.split(" ", 1)[1]
        except IndexError:
            await message.reply("يرجى إرسال رابط بعد /dl")
            return
        wait_msg = await message.reply("جارٍ تحميل الصوت، انتظر لحظة...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                audio_path = os.path.splitext(filename)[0] + ".mp3"

            await client.send_audio(
                chat_id=message.chat.id,
                audio=audio_path,
                reply_to_message_id=message.id
            )
        except Exception as e:
            await message.reply(f"حدث خطأ أثناء التحميل: {e}")
        finally:
            print(wait_msg)
            await app.delete_messages(message.chat.id,wait_msg.id)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        return

    elif text == "/getthisid":
        await message.reply(f"Chat ID: {message.chat.id}")

    elif text == "/harakat":
        if not message.reply_to_message or not message.reply_to_message.text:
            await message.reply("رد على رسالة بيها نص حتى أشكلها.")
            return

        original = message.reply_to_message.text
        harakat = vocalizer.tashkeel(original)
        await message.reply(harakat)


if __name__ == "__main__":
    app.run()
