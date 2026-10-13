import sys
import requests
from config import BOT_TOKEN, CHAT_ID


def send(text: str):
    if not CHAT_ID:
        raise RuntimeError(
            "STOCK_CHAT_ID 尚未設定。先在 Telegram 找 @Chi017_bot 傳一則訊息，"
            "再執行 fetch_chat_id.py 取得 chat_id，填進根目錄 .env 的 STOCK_CHAT_ID。"
        )
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text},
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "測試訊息：017 股市推播已連通"
    print(send(message))
