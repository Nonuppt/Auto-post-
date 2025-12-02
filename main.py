import logging
import requests
import asyncio
import sys

try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, Application
    from telegram.error import Conflict
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "python-telegram-bot package not found. Install dependencies with 'pip install -r requirements.txt'."
    ) from e

# ----- USER CONFIG -----
# REPLACE THIS WITH YOUR *NEW* TOKEN FROM BOTFATHER
BOT_TOKEN = "8488614783:AAE4Z1GZDYxaDMMxOc9Owofbpw3kaokPIHs" 
TMDB_API = "c5b6317ff1ba730c5742a94440d31af4"

DB_CHANNEL = -1002837138676
MOVIE_CHANNEL = -1002481569627
SERIES_CHANNEL = -1002414133579

DOWNLOAD_LINK = "https://t.me/+FnbegV_ohyo4YzE1"
BACKUP_LINK = "http://t.me/Pixell_Pulse"
# ------------------------

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def search_tmdb(query: str):
    """Synchronous TMDB search helper."""
    try:
        url = "https://api.themoviedb.org/3/search/multi"
        params = {"api_key": TMDB_API, "query": query}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data_json = r.json()
    except Exception:
        logging.error("TMDB request failed")
        return None

    results = data_json.get("results") or []
    if not results:
        return None

    data = results[0]
    poster = f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else None
    title = data.get("title") or data.get("name")
    media_type = data.get("media_type")

    return {"title": title, "poster": poster, "type": media_type}


async def handle_db_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or msg.chat.id != DB_CHANNEL:
        return

    text = msg.caption or msg.text
    if not text:
        return

    tmdb = await asyncio.to_thread(search_tmdb, text)
    if not tmdb:
        return

    target = MOVIE_CHANNEL if tmdb["type"] == "movie" else SERIES_CHANNEL
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download Now", url=DOWNLOAD_LINK)],
        [InlineKeyboardButton("Join Backup 🎯", url=BACKUP_LINK)],
    ])

    caption = f"**{tmdb['title']}**\n\n📥 Download Now 👇"

    try:
        await context.bot.send_photo(
            chat_id=target,
            photo=tmdb["poster"],
            caption=caption,
            reply_markup=buttons,
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(f"Failed to send photo: {e}")

async def post_init(application: Application):
    bot_info = await application.bot.get_me()
    logging.info("--------------------------------------------------")
    logging.info(f"✅ BOT STARTED SUCCESSFULLY!")
    logging.info(f"🤖 Bot Username: @{bot_info.username}")
    logging.info(f"🆔 Bot ID: {bot_info.id}")
    logging.info("--------------------------------------------------")

def main():
    if BOT_TOKEN == "YOUR_NEW_TOKEN_HERE":
        logging.critical("❌ ERROR: You must update BOT_TOKEN with the new token from BotFather!")
        sys.exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(MessageHandler(filters.ALL, handle_db_post))
    
    logging.info("Initializing Bot...")
    
    try:
        app.run_polling(drop_pending_updates=True)
    except Conflict:
        logging.critical("--------------------------------------------------")
        logging.critical("🛑 CRITICAL ERROR: CONFLICT DETECTED")
        logging.critical("Another instance of this bot is already running!")
        logging.critical("SOLUTION: Revoke your Bot Token in @BotFather and update the code.")
        logging.critical("--------------------------------------------------")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
