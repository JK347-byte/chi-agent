import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

SHEET_TAB = "台股資產配置監控總表"


def open_sheet(credentials_file: str, spreadsheet_id: str):
    creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    gc = gspread.authorize(creds)
    ss = gc.open_by_key(spreadsheet_id)
    return ss.worksheet(SHEET_TAB)
