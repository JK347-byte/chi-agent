"""一次性執行：設定自動換算公式、日期格式、日期選擇器"""
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


def main():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    ss = gc.open_by_key(SHEET_ID)
    ws = ss.worksheet("個案總表")
    sheet_id = ws.id

    # ① G 欄自動換算公式：下次最早可回診日 = 最近回診日 + 追蹤間隔（天）
    formulas = [[f'=IF(AND(E{r}<>"",F{r}<>""),E{r}+F{r},"")'] for r in range(2, 501)]
    ws.update("G2:G500", formulas, value_input_option="USER_ENTERED")
    print("✅ 自動換算公式已設定（G = 最近回診日 + 追蹤間隔）")

    requests = []

    # ② D、E、G 欄格式設為日期（避免顯示成數字）
    for col_idx in (3, 4, 6):  # D=3, E=4, G=6（0-based）
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 500,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "DATE", "pattern": "yyyy/mm/dd"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        })

    # ③ D（收案日期）、E（最近回診日）加上日期選擇器
    for col_idx in (3, 4):
        requests.append({
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 500,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                },
                "rule": {
                    "condition": {"type": "DATE_IS_VALID"},
                    "showCustomUi": True,
                },
            }
        })

    ss.batch_update({"requests": requests})
    print("✅ 日期格式已設定（D、E、G 欄）")
    print("✅ 日期選擇器已設定（D 收案日期、E 最近回診日）")
    print("\n請重新整理 Google Sheets 頁面，點 D 或 E 欄格子即可看到日曆圖示")


if __name__ == "__main__":
    main()
