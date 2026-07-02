"""一次性執行：在個案總表「專案」欄加入下拉選單"""
import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

SHEET_ID   = "1sDLebrYzWbLoFB8S37Q7vY6XuzJd_ukZyNYcXzItTHw"
CREDS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
PROJECTS   = ["代謝症候群", "氣喘", "疫苗", "口腔篩檢"]
PROJECT_COL = 2  # 0-based，第 C 欄 = 專案


def main():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    ss = gc.open_by_key(SHEET_ID)
    ws = ss.worksheet("個案總表")
    sheet_id = ws.id

    request = {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,       # 從第 2 列開始（跳過標題）
                "endRowIndex": 500,
                "startColumnIndex": PROJECT_COL,
                "endColumnIndex": PROJECT_COL + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": p} for p in PROJECTS],
                },
                "showCustomUi": True,     # 顯示下拉箭頭
                "strict": True,           # 禁止輸入清單以外的值
            },
        }
    }

    ss.batch_update({"requests": [request]})
    print("✅ 下拉選單已建立，選項：")
    for p in PROJECTS:
        print(f"  • {p}")


if __name__ == "__main__":
    main()
