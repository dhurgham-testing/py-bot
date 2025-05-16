import asyncio

from telebot.async_telebot import AsyncTeleBot

bot = AsyncTeleBot('7942007970:AAHNdBFQ6EC9ScrCjJSCl8lA0hGKi101q6U')


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)



@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)

print('bot started')
asyncio.run(bot.polling())
