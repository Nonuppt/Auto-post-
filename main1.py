import logging
import requests
from telegram import Bot, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# ----- USER CONFIG -----
BOT_TOKEN = "8488614783:AAE4Z1GZDYxaDMMxOc9Owofbpw3kaokPIHs"
TMDB_API = "c5b6317ff1ba730c5742a94440d31af4"

DB_CHANNEL = -1002837138676
MOVIE_CHANNEL = -1002481569627
SERIES_CHANNEL = -1002414133579

DOWNLOAD_LINK = "https://t.me/+FnbegV_ohyo4YzE1"
BACKUP_LINK = "http://t.me/Pixell_Pulse"
# ------------------------

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)


def search_tmdb(query):
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API}&query={query}"
    r = requests.get(url).json()

    if not r["results"]:
        return None

    data = r["results"][0]

    poster = f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else None
    title = data.get("title") or data.get("name")
    type_media = data.get("media_type")   # movie or tv

    return {
        "title": title,
        "poster": poster,
        "type": type_media
    }


async def handle_db_post(update, context):
    msg = update.message

    if msg.chat.id != DB_CHANNEL:
        return

    text = msg.caption or msg.text
    if not text:
        return

    tmdb = search_tmdb(text)
    if not tmdb:
        return

    title = tmdb["title"]
    poster = tmdb["poster"]
    media_type = tmdb["type"]

    # Select channel
    if media_type == "movie":
        target = MOVIE_CHANNEL
    else:
        target = SERIES_CHANNEL

    # Buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download Now", url=DOWNLOAD_LINK)],
        [InlineKeyboardButton("Join Backup 🎯", url=BACKUP_LINK)]
    ])

    # Send Poster + Caption
    caption = f"**{title}**\n\n📥 Download Now 👇"

    await bot.send_photo(
        chat_id=target,
        photo=poster,
        caption=caption,
        reply_markup=buttons,
        parse_mode="Markdown"
    )


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_db_post))
    print("Bot is running...")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
