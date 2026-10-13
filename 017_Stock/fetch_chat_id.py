import requests
from config import BOT_TOKEN

resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates").json()
updates = resp.get("result", [])

if not updates:
    print("還沒收到任何訊息。先在 Telegram 找 @Chi017_bot，傳一則訊息給它，再重新執行這支腳本。")
else:
    for u in updates:
        chat = u["message"]["chat"]
        name = chat.get("first_name") or chat.get("title") or ""
        print(f"chat_id={chat['id']}  name={name}")
