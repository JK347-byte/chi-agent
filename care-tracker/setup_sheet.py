"""執行一次，建立 Google Sheets 結構"""
import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

SHEET_ID = "1sDLebrYzWbLoFB8S37Q7vY6XuzJd_ukZyNYcXzItTHw"

MAIN_HEADERS   = ["病歷號", "姓名", "專案", "收案日期", "最近回診日",
                  "追蹤間隔（天）", "下次最早可回診日", "狀態", "備註", "最後更新", "更新者"]
RECORD_HEADERS = ["病歷號", "姓名", "專案", "回診日期", "備註", "記錄時間", "記錄者"]


def main():
    creds = Credentials.from_service_account_file(
        os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"), scopes=SCOPES)
    gc = gspread.authorize(creds)
    ss = gc.open_by_key(SHEET_ID)
    print(f"✅ 已連線試算表：{ss.title}")

    # 個案總表
    try:
        ws = ss.worksheet("個案總表")
        print("找到現有工作表：個案總表")
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet("個案總表", rows=500, cols=15)
        print("已新增工作表：個案總表")
    ws.update("A1", [MAIN_HEADERS])
    ws.format("A1:K1", {
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "backgroundColor": {"red": 0.16, "green": 0.40, "blue": 0.69},
    })
    ws.freeze(rows=1)

    # 回診記錄
    try:
        rs = ss.worksheet("回診記錄")
        print("找到現有工作表：回診記錄")
    except gspread.WorksheetNotFound:
        rs = ss.add_worksheet("回診記錄", rows=2000, cols=10)
        print("已新增工作表：回診記錄")
    rs.update("A1", [RECORD_HEADERS])
    rs.format("A1:G1", {
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "backgroundColor": {"red": 0.13, "green": 0.55, "blue": 0.33},
    })
    rs.freeze(rows=1)

    # 移除預設工作表
    for name in ("工作表1", "Sheet1"):
        try:
            ss.del_worksheet(ss.worksheet(name))
            print(f"已移除預設工作表：{name}")
        except Exception:
            pass

    print(f"\n✅ 設定完成！")
    print(f"試算表網址：https://docs.google.com/spreadsheets/d/{SHEET_ID}")


if __name__ == "__main__":
    main()
