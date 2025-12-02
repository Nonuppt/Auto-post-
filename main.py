import logging
import requests
import asyncio

try:
    from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, Application
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "python-telegram-bot package not found. Install dependencies with 'pip install -r requirements.txt' or run 'pip install python-telegram-bot'."
    ) from e

# ----- USER CONFIG -----
# CRITICAL SECURITY WARNING: Ideally, load these from environment variables (os.getenv)
BOT_TOKEN = "8488614783:AAEBAdRDEnRL3G7QafCp8Hp81LPyypni8go"
TMDB_API = "c5b6317ff1ba730c5742a94440d31af4"

DB_CHANNEL = -1002837138676
MOVIE_CHANNEL = -1002481569627
SERIES_CHANNEL = -1002414133579

DOWNLOAD_LINK = "https://t.me/+FnbegV_ohyo4YzE1"
BACKUP_LINK = "http://t.me/Pixell_Pulse"
# ------------------------

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def search_tmdb(query: str):
    """Synchronous TMDB search helper. Returns dict or None."""
    try:
        url = "https://api.themoviedb.org/3/search/multi"
        params = {"api_key": TMDB_API, "query": query}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data_json = r.json()
    except Exception:
        logging.exception("TMDB request failed")
        return None

    results = data_json.get("results") or []
    if not results:
        return None

    data = results[0]
    poster = f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else None
    title = data.get("title") or data.get("name")
    type_media = data.get("media_type")   # movie or tv

    return {
        "title": title,
        "poster": poster,
        "type": type_media
    }


async def handle_db_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    if msg.chat.id != DB_CHANNEL:
        return

    text = msg.caption or msg.text
    if not text:
        return

    # Run blocking HTTP call in a thread to avoid blocking the event loop
    tmdb = await asyncio.to_thread(search_tmdb, text)
    if not tmdb:
        return

    title = tmdb["title"]
    poster = tmdb["poster"]
    media_type = tmdb["type"]

    # Select channel
    target = MOVIE_CHANNEL if media_type == "movie" else SERIES_CHANNEL

    # Buttons
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📥 Download Now", url=DOWNLOAD_LINK)],
            [InlineKeyboardButton("Join Backup 🎯", url=BACKUP_LINK)],
        ]
    )

    # Send Poster + Caption
    caption = f"**{title}**\n\n📥 Download Now 👇"

    try:
        await context.bot.send_photo(
            chat_id=target,
            photo=poster,
            caption=caption,
            reply_markup=buttons,
            parse_mode="Markdown",
        )
    except Exception:
        logging.exception("Failed to send photo")

# --- NEW FUNCTION: Runs immediately after bot connects ---
async def post_init(application: Application):
    """
    This function runs after the bot is initialized but before polling starts.
    It fetches the bot's info and prints the username.
    """
    bot_info = await application.bot.get_me()
    logging.info("--------------------------------------------------")
    logging.info(f"✅ BOT STARTED SUCCESSFULLY!")
    logging.info(f"🤖 Bot Username: @{bot_info.username}")
    logging.info(f"🆔 Bot ID: {bot_info.id}")
    logging.info("--------------------------------------------------")

def main():
    # Added .post_init(post_init) to the builder
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(MessageHandler(filters.ALL, handle_db_post))
    
    logging.info("Initializing Bot...")
    # allowed_updates is set to handle everything; adjust if needed for performance
    app.run_polling(drop_pending_updates=True) 

if __name__ == "__main__":
    main()
