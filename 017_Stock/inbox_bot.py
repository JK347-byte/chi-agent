import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from config import BOT_TOKEN, CHAT_ID

BASE_DIR = Path(__file__).parent
NOTE_FILE = Path(
    "/Users/janskey/Documents/Obsidian Vault/NumbersOffice/017_Stock/股市資訊收集.md"
)
TAIPEI_TZ = ZoneInfo("Asia/Taipei")

logging.basicConfig(
    filename=BASE_DIR / "inbox_bot.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


def ensure_note():
    if not NOTE_FILE.exists():
        NOTE_FILE.write_text(
            "# 017 股市資訊收集\n\n"
            "詹醫師透過 Telegram（@Chi017_bot）傳進來的股票相關資訊，依時間先後記錄。"
            "單純收集，整理/比較在對話中依詹醫師需求進行，不自動分析。\n\n"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(CHAT_ID):
        return
    text = update.message.text
    if not text:
        return

    ensure_note()
    timestamp = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M")
    with NOTE_FILE.open("a", encoding="utf-8") as f:
        f.write(f"## {timestamp}\n{text}\n\n")

    logging.info("記錄一筆訊息：%s", text[:50])
    await update.message.reply_text("✅ 已記錄")


def main():
    ensure_note()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("inbox_bot 啟動")
    app.run_polling()


if __name__ == "__main__":
    main()
