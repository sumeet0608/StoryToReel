import os, logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from utils import ensure_dirs
from reddit_fetch import extract_text_from_input

logging.basicConfig(filename="../logs.txt",encoding='utf-8',level=logging.INFO, format="[%(levelname)s] %(message)s")
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise SystemExit("Missing TELEGRAM_BOT_TOKEN in .env")

ensure_dirs(["data/gameplay", "temp", "output"])

HELP_TEXT = (
    "Send /story followed by a Reddit link or pasted text.\n"
    "Example: /story https://www.reddit.com/r/AmItheAsshole/comments/...\n"
    "I will reply with script.txt, voice.mp3, and reel.mp4"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)

async def handle_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (update.message.text or "").strip()
    try:
        await update.message.reply_text("Extracting text...")
        raw_text = await extract_text_from_input(msg)
        if not raw_text or len(raw_text.strip()) < 40:
            raise ValueError("Couldn't extract enough text. Paste a link or longer text.")
        
        # 2) Summarize + punch up into reel script
        await update.message.reply_text("Generating script...")
        script_text = make_reel_script(raw_text, target_words=175)
        
    except Exception as e:
        logging.exception("/story failed")
        await update.message.reply_text(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("story", handle_story))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()