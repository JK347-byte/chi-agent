import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_DIARY_TOKEN = os.getenv("TELEGRAM_DIARY_TOKEN")
INBOX_DIR = "/Users/janskey/Documents/Obsidian Vault/NumbersOffice/006_Diary/inbox"
ASSETS_DIR = "/Users/janskey/Documents/Obsidian Vault/NumbersOffice/006_Diary/assets"

logging.basicConfig(level=logging.INFO)


def write_inbox(content: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(INBOX_DIR, f"tel_{timestamp}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    write_inbox(f"[{now}] {text}")

    await update.message.reply_text("📓 日記已收，今晚自動整理。")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    photo = update.message.photo[-1]
    file = await photo.get_file()
    filename = f"diary_{timestamp}.jpg"
    filepath = os.path.join(ASSETS_DIR, filename)
    await file.download_to_drive(filepath)

    caption = update.message.caption.strip() if update.message.caption else ""
    content = f"[{now}] [圖片] ![[{filename}]]"
    if caption:
        content += f" {caption}"
    write_inbox(content)

    await update.message.reply_text("🖼️ 圖片已收，今晚自動整理。")


def main():
    app = Application.builder().token(TELEGRAM_DIARY_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("✅ 006 日記 Bot 啟動中...")
    app.run_polling()


if __name__ == "__main__":
    main()
