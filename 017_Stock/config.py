import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("STOCK_BOT_TOKEN")
CHAT_ID = os.getenv("STOCK_CHAT_ID")
