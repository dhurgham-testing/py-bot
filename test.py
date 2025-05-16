from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Store channel messages in-memory (message_id: message object)
channel_messages = {}

CHANNEL_ID = -1002664680052  # Telegram channel IDs are negative for supergroups/channels

async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save new channel messages for searching later
    msg = update.channel_post
    if msg:
        channel_messages[msg.message_id] = msg

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User sends /search <keyword>
    if not context.args:
        await update.message.reply_text("Please provide a keyword to search, e.g. /search blabla")
        return
    
    keyword = " ".join(context.args).lower()
    found_messages = []

    # Search stored messages text for keyword
    for msg_id, msg in channel_messages.items():
        if msg.text and keyword in msg.text.lower():
            found_messages.append(msg)

    if not found_messages:
        await update.message.reply_text(f"No messages found with keyword: {keyword}")
        return

    # Forward all found messages back to user
    for msg in found_messages:
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=CHANNEL_ID,
            message_id=msg.message_id
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /search <keyword> to search channel messages.")

if __name__ == '__main__':
    TOKEN = '7942007970:AAHNdBFQ6EC9ScrCjJSCl8lA0hGKi101q6U'

    app = ApplicationBuilder().token(TOKEN).build()

    # Listen for posts in the channel (only if bot is admin and receives updates)
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_post_handler))

    # Command for search
    app.add_handler(CommandHandler("search", search_command))

    # Start command
    app.add_handler(CommandHandler("start", start))

    print("Bot started...")
    app.run_polling()
