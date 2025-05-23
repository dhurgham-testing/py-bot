import os
import uuid
import yt_dlp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from mishkal import tashkeel
import httpx


api_id = 1040477
api_hash = "ba3c1b7bbd8de520d2adb0e1187f5622"
openrouter_api_key = "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"


app = Client("search_bot", api_id=api_id, api_hash=api_hash)
CHANNEL_ID = -1002664680052
ALLOWED_USERS = [959599690, 996193663]
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
tashkel = tashkeel
vocalizer =tashkel.TashkeelClass()
groq_api_key = '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'
groq_url = "https://api.groq.com/openai/v1/chat/completions"
async def ask_groq_chat(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    json_data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 1,
        "n": 1,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(groq_url, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


# لتنظيف عنوان الفيديو حتى يصير اسم ملف صالح
def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in "._- ").strip()

@app.on_message(filters.private & filters.text)
async def handle_commands(client: Client, message: Message):
    if message.from_user.id not in ALLOWED_USERS:
        return

    # if message.from_user.id == 959599690 and message.chat.id == 996193663:
    #     harakat = vocalizer.tashkeel(message.text)
    #     if harakat != message.text:
    #         await app.edit_message_text(message.chat.id, message.id, harakat)

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
    elif text.startswith("سوي صوت"):
        try:
            url = text.split(" ", 2)[2]
        except IndexError:
            await message.reply("ارسل الرابط بعد 'سوي صوت'")
            return

        wait_msg = await message.reply("جارٍ تحميل الصوت...")

        random_name = str(uuid.uuid4())
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"{DOWNLOAD_DIR}/{random_name}.%(ext)s",
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
                title = info.get("title", "الصوت")
                audio_path = os.path.join(DOWNLOAD_DIR, f"{random_name}.mp3")

            await client.send_audio(
                chat_id=message.chat.id,
                audio=audio_path,
                caption=title,
                reply_to_message_id=message.id
            )
        except Exception as e:
            await message.reply(f"صار خطأ بالتحميل: {e}")
        finally:
            await app.delete_messages(message.chat.id, wait_msg.id)
            if os.path.exists(audio_path):
                os.remove(audio_path)

    # 🎥 تحميل الفيديو
    elif text.startswith("سوي فيديو"):
        try:
            url = text.split(" ", 2)[2]
        except IndexError:
            await message.reply("ارسل الرابط بعد 'سوي فيديو'")
            return

        wait_msg = await message.reply("جارٍ تحميل الفيديو...")

        random_name = str(uuid.uuid4())
        ydl_opts = {
            'format': 'best',
            'outtmpl': f"{DOWNLOAD_DIR}/{random_name}.%(ext)s",
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "الفيديو")
                ext = info.get("ext", "mp4")
                video_path = os.path.join(DOWNLOAD_DIR, f"{random_name}.{ext}")

            await client.send_video(
                chat_id=message.chat.id,
                video=video_path,
                caption=title,
                reply_to_message_id=message.id
            )
        except Exception as e:
            await message.reply(f"صار خطأ بالتحميل: {e}")
        finally:
            await app.delete_messages(message.chat.id, wait_msg.id)
            if os.path.exists(video_path):
                os.remove(video_path)

    elif text.startswith("ذكاء نص ردن"):
        if len(text.split(" ", 2)) < 3:
            await message.reply("اكتب السؤال بعد 'ذكاء نص ردن'")
            return

        question = text.split(" ", 3)[3]
        wait_msg = await message.reply("جاري التفكير 💭...")

        answer = await ask_groq_chat(question)
        await message.reply(answer)
        await wait_msg.delete()


    elif text == "/analyse":
        if not message.reply_to_message:
            await message.reply("يرجى الرد على رسالة لتحديد بداية التحليل.")
            return

        start_id = message.reply_to_message.id
        end_id = message.id
        chat_id = message.chat.id

        if end_id < start_id:
            await message.reply("رسالة /analyze يجب أن تكون بعد الرسالة التي تم الرد عليها.")
            return

        messages = []
        async for msg in client.get_chat_history(chat_id, offset_id=end_id):
            if msg.id < start_id:
                break
            if not getattr(msg, "empty", False):
                messages.append(msg)

        if not messages:
            await message.reply("لم يتم العثور على رسائل في النطاق المحدد.")
            return

        texts = [msg.text or "" for msg in reversed(messages)]

        prompt = (
                "من هذه رسائلنا، ماذا تظن نحن؟ هل نحن جدد؟ أعطنا رأيك الجيد والسيئ:\n\n"
                + "\n".join(texts)
        )

        wait_msg = await message.reply("جاري تحليل الرسائل...")

        try:
            answer = await ask_groq_chat(prompt)
            await message.reply(answer)
        except Exception as e:
            await message.reply(f"حدث خطأ أثناء الاتصال بـ Groq AI: {e}")
        finally:
            await wait_msg.delete()

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
