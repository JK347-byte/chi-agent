import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
QUEUE_FILE = "/Users/janskey/Documents/Obsidian Vault/NumbersOffice/queue.md"

LABELS = {"006": "日記", "007": "醫學", "008": "財務"}
MENU_TEXT = """NumbersOffice 選單

006 日記助理 — 記錄日常生活、心情、想法
007 醫學知識助理 — 整理臨床筆記、醫學討論、文獻重點
008 財務記帳助理 — 記錄收支、管理財務目標

輸入 006 / 007 / 008 + 內容即可排隊。"""

logging.basicConfig(level=logging.INFO)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "1":
        await update.message.reply_text(MENU_TEXT)
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    prefix = text[:3]
    label = LABELS.get(prefix, "訊息")

    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(f"- [{now}] {text}\n")

    await update.message.reply_text(f"✅ {label}已排隊，回到電腦後自動處理。")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("✅ NumbersOffice Bot 啟動中...")
    app.run_polling()


if __name__ == "__main__":
    main()
