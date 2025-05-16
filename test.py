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


# لتنظيف عنوان الفيديو حتى يصير اسم ملف صالح
def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in "._- ").strip()

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

    # 🔊 تحميل صوت
    elif text.startswith("/audio "):
        url = text.split(" ", 1)[1]
        wait_msg = await message.reply("جارٍ تحميل الصوت، انتظر لحظة...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
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
                title = sanitize_filename(info.get("title", "audio"))
                audio_path = f"downloads/{title}.mp3"

            await client.send_audio(
                chat_id=message.chat.id,
                audio=audio_path,
                caption=title,
                reply_to_message_id=message.id
            )
        except Exception as e:
            await message.reply(f"حدث خطأ أثناء التحميل: {e}")
        finally:
            await app.delete_messages(message.chat.id, wait_msg.id)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        return

    # 📹 تحميل فيديو
    elif text.startswith("/video "):
        url = text.split(" ", 1)[1]
        wait_msg = await message.reply("جارٍ تحميل الفيديو، انتظر لحظة...")

        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get("title", "video"))
                ext = info.get("ext", "mp4")
                video_path = f"downloads/{title}.{ext}"

            await client.send_video(
                chat_id=message.chat.id,
                video=video_path,
                caption=title,
                reply_to_message_id=message.id
            )
        except Exception as e:
            await message.reply(f"حدث خطأ أثناء التحميل: {e}")
        finally:
            await app.delete_messages(message.chat.id, wait_msg.id)
            if os.path.exists(video_path):
                os.remove(video_path)
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
