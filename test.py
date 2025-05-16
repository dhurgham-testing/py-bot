import asyncio
import json

from telebot.async_telebot import AsyncTeleBot

bot = AsyncTeleBot('7942007970:AAHNdBFQ6EC9ScrCjJSCl8lA0hGKi101q6U')


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)


@bot.message_handler(commands=['search'])
async def handle_search(message):
    # Extract the keyword from the command
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await bot.reply_to(message, "❗ Please provide a search keyword after /search.")
        return
    keyword = parts[1].strip().lower()

    # Ensure the message is a reply to another message
    if not message.reply_to_message:
        await bot.reply_to(message, "❗ Please reply to a forwarded message from the channel to search.")
        return

    fwd = message.reply_to_message

    # Check if the replied message is a forwarded message from a channel
    if not fwd.forward_from_chat or fwd.forward_from_chat.type != 'channel':
        await bot.reply_to(message, "❗ The replied message is not a forwarded message from a channel.")
        return

    # Get the content of the forwarded message (text or caption)
    content = fwd.text or fwd.caption or ''
    if keyword in content.lower():
        # Copy the original message back to the user
        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=fwd.forward_from_chat.id,
            message_id=fwd.forward_from_message_id
        )
    else:
        await bot.reply_to(message, "❌ No match found in the forwarded message.")

print("Bot started.")
asyncio.run(bot.polling())

print('bot started')
asyncio.run(bot.polling())
