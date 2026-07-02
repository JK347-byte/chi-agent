"""一次性執行：在個案總表建立四個命名篩選檢視"""
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

SHEET_ID  = "1sDLebrYzWbLoFB8S37Q7vY6XuzJd_ukZyNYcXzItTHw"
CREDS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
PROJECT_COL = 2  # 個案總表第 C 欄（0-based）= 專案

PROJECTS = ["代謝症候群", "氣喘", "疫苗", "口腔篩檢"]


def main():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    ss = gc.open_by_key(SHEET_ID)
    ws = ss.worksheet("個案總表")
    sheet_id = ws.id

    requests = [
        {
            "addFilterView": {
                "filter": {
                    "title": project,
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "startColumnIndex": 0,
                        "endColumnIndex": 11,
                    },
                    "criteria": {
                        str(PROJECT_COL): {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": project}],
                            }
                        }
                    },
                }
            }
        }
        for project in PROJECTS
    ]

    ss.batch_update({"requests": requests})
    print("✅ 已建立篩選檢視：")
    for p in PROJECTS:
        print(f"  • {p}")


if __name__ == "__main__":
    main()
