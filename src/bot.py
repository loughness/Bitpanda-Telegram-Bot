import logging
import os
import json

from dotenv import load_dotenv
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler
from uuid import uuid4

from bitpanda import BitpandaClient
from database import store_api_key, get_api_key, delete_api_key, setup_database

load_dotenv()
api_token = os.getenv('BOT_TOKEN')
USER_DATE_FILE = "user_data.json"

# This sets up the logging module
# this will give insight into when and why things are not working as expected
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def load_users():
    if not os.path.exists(USER_DATE_FILE):
        return {}
    with open(USER_DATE_FILE, 'r') as file:
        return json.load(file)
    
def save_users(users):
    with open(USER_DATE_FILE, 'w') as file:
        json.dump(users, file)

def get_start_message():
    return """
👋 *Welcome to Bitpanda Portfolio Bot!* 📊
---------------------------------------------

I’m here to help you track your *Bitpanda portfolio* easily via Telegram.

🚀 *What You Can Do:*
🔹 Check your *total balance* across all assets.
🔹 View *profit/loss* for specific cryptocurrencies.
🔹 Get *live prices* for your favorite coins.
🔹 Set up *price alerts* for market movements.
🔹 Securely *log in* and *log out* with your API key.

📌 *Getting Started:*
1️⃣ First, log in by sending:  
   `/login YOUR_BITPANDA_API_KEY`
2️⃣ Once logged in, try:
   - `/balance` → See your total balance.
   - `/profit BTC --7d` → Check Bitcoin profit in the last 7 days.
   - `/price ETH` → Get the latest Ethereum price.

🛠 *Need Help?*
Type `/help` at any time for a list of available commands.

Happy trading! 🚀💰
    """

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_message = get_start_message()

    users = load_users()
    user_id = str(update.effective_user.id)

    if user_id not in users:
        # this means they are a first time user
        users[user_id] = {"first_seen": update.effective_message.date.isoformat()}
        save_users(users)
    
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=start_message,
            parse_mode="Markdown"
        )
    else:
        # Returning user
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Welcome back!\n" + start_message,
            parse_mode='Markdown'
        )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_menu = """
🤖 *Welcome to the Bitpanda Portfolio Bot!* 📊
---------------------------------------------

This bot helps you track your cryptocurrency, stocks, and precious metals on *Bitpanda* with simple commands.

🛠 *Available Commands:*
🔹 `/start` - Get a warm welcome and setup instructions.
🔹 `/balance` - Show your *total account balance* across all assets.
🔹 `/balance BTC` - Get your *Bitcoin balance* and its current value.
🔹 `/profit BTC --7d` - Show your *Bitcoin profit/loss* in the last 7 days.
🔹 `/profit --all-time` - Display *all-time profit/loss* for your entire portfolio.
🔹 `/price ETH` - Fetch the *current Ethereum price* from Bitpanda.
🔹 `/alerts BTC 40000` - Set a price alert for Bitcoin at *40,000 EUR*.
🔹 `/logout` - Securely log out and remove stored API keys.

⚡ *Example Queries You Can Ask:*
💬 _"What is my total balance?"_
💬 _"How much money have I made on Ethereum this month?"_
💬 _"Tell me if Bitcoin drops below 40k."_

📌 Need more help? Type `/help` anytime!
    """
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_menu,
        parse_mode="Markdown"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

async def inline_share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return

    # Advertisement message for users to share
    share_message = """
🚀 *Check out the Bitpanda Portfolio Bot!* 📊

Looking for an easy way to track your *Bitpanda portfolio* directly on Telegram?  
This bot helps you:
✅ View your *balance & profit/loss*  
✅ Get *real-time crypto prices*  
✅ Set up *price alerts*  

Try it now! 👉 [Click here to chat with the bot](https://t.me/bitpanda_portfolio_bot)

💡 Just type `@bitpanda_portfolio_bot share` in any chat to share this!
    """

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="📢 Share Bitpanda Bot",
            description="Share this message to promote the bot!",
            input_message_content=InputTextMessageContent(
                share_message, parse_mode="Markdown"
            )
        )
    ]

    await update.inline_query.answer(results, cache_time=1)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    try:
        # retrieve the API key and initialise the client
        client = BitpandaClient(user_id)
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ You need to log in first using `/login YOUR_API_KEY`",
            parse_mode="Markdown"
        )
        return

    if context.args:
        asset = context.args[0].upper() 
        # then to fetch the balance for the asset
        asset_balance_message = client.get_asset_balances()
        fiat_balance_message = client.get_fiat_balances()

        # filter to specific asset
        # Combine asset and fiat balance messages
        if asset in asset_balance_message:
            balance_message = "\n".join([line for line in asset_balance_message.split("\n") if asset in line])
        elif asset in fiat_balance_message:
            balance_message = "\n".join([line for line in fiat_balance_message.split("\n") if asset in line])
        else:
            balance_message = f"❌ No balance found for {asset}."

        message = f"🔍 *{asset} Balance:*\n{balance_message}"

    else: 
        # if no asset is provided, need to show total balance
        asset_balance_message = client.get_asset_balances()
        fiat_balance_message = client.get_fiat_balances()
        message = asset_balance_message + "\n" + fiat_balance_message

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode='Markdown'
    )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # this gets the user_id for storing in the database
    user_id = str(update.effective_user.id)

    if context.args:
        api_key = context.args[0]
        store_api_key(user_id=user_id, api_key=api_key)
        message = (
            "✅ *Login Successful!* \n\n"
            "Your API key has been securely stored. \n"
            "🚨 *For security reasons, please delete this chat message now!*"
        )
    else:
        message = "⚠️ *You need to supply your API key to log in.*\nUsage: `/login YOUR_BITPANDA_API_KEY`"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode='Markdown'
    )

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # getting the user_id to delete key from db
    user_id = str(update.effective_user.id)
    delete_api_key(user_id=user_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ You have been logged out. Your API key has been removed securely.",
        parse_mode="Markdown"
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. Type /help for more info")


if __name__ == '__main__':
    application = ApplicationBuilder().token(api_token).build()
    setup_database()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), unknown)
    caps_handler = CommandHandler('caps', caps)
    help_handler = CommandHandler('help', help)
    balance_handler = CommandHandler('balance', balance)

    login_handler = CommandHandler('login', login)
    logout_handler = CommandHandler('logout', logout)

    inline_share_handler = InlineQueryHandler(inline_share)
    application.add_handler(inline_share_handler)


    # Unkown handler to be added last
    # if used before it would trigger before the other command handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(help_handler)
    application.add_handler(balance_handler)

    application.add_handler(login_handler)
    application.add_handler(logout_handler)

    application.add_handler(unknown_handler)

    application.run_polling()