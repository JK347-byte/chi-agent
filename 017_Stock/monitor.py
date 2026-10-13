import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from notify import send
from sheets_client import open_sheet

BASE_DIR = Path(__file__).parent
CREDS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", str(BASE_DIR.parent / "care-tracker" / "credentials.json"))
SPREADSHEET_ID = "1BZw_NRQMqClJIrLhVNffyohU0t-oh00-lWnGQvaglyA"
STATE_FILE = BASE_DIR / "signal_state.json"
POLL_SECONDS = 30 * 60  # 每 30 分鐘檢查一次
TAIPEI_TZ = ZoneInfo("Asia/Taipei")

logging.basicConfig(
    filename=BASE_DIR / "monitor.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)

# 用文字比對找列號，不寫死儲存格位址——表格常被增刪列，位址會位移
# (標籤文字, 標籤欄, 數值欄)　欄號1-based：A=1 B=2 ... F=6 G=7
SIGNAL_LABELS = {
    "pyramid":       ("正金字塔加倉", 1, 2),   # QQQ，只在A欄找，避免誤配到SOXX那個
    "soxx_pyramid":  ("SOXX正金字塔加倉", 6, 7),
    "deviation":     ("乖離過大操作訊號", 1, 2),
    "annual":        ("年度操作訊號", 1, 2),
}

TOTAL_LABEL = "合併總資產總計"
YESTERDAY_LABEL = "前一日總資產"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def _find_row(col: list, needle: str):
    for i, cell in enumerate(col):
        if needle in cell:
            return i + 1  # gspread 是1-based列號
    return None


def find_signals(ws) -> dict:
    """依SIGNAL_LABELS指定的欄位找標籤所在列，讀同列的數值欄。回傳 {key: (label文字, 值)}"""
    col_cache = {}
    found = {}
    for key, (needle, label_col, value_col) in SIGNAL_LABELS.items():
        if label_col not in col_cache:
            col_cache[label_col] = ws.col_values(label_col)
        col = col_cache[label_col]
        row = _find_row(col, needle)
        if row is None:
            continue
        if value_col not in col_cache:
            col_cache[value_col] = ws.col_values(value_col)
        value_col_data = col_cache[value_col]
        label = col[row - 1].strip()
        value = (value_col_data[row - 1].strip() if row - 1 < len(value_col_data) else "")
        found[key] = (label, value)
    return found


def daily_snapshot(ws, state: dict):
    """每天第一次檢查時，把「合併總資產總計」寫進「前一日總資產」，當作明天比較的基準"""
    today = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d")
    if state.get("last_snapshot_date") == today:
        return state

    col_a = ws.col_values(1)
    col_d = ws.col_values(4)
    total_row = _find_row(col_a, TOTAL_LABEL)
    yesterday_row = _find_row(col_a, YESTERDAY_LABEL)
    if not total_row or not yesterday_row:
        logging.warning("找不到 %s 或 %s，略過每日快照", TOTAL_LABEL, YESTERDAY_LABEL)
        return state

    total_value = col_d[total_row - 1] if total_row - 1 < len(col_d) else None
    if not total_value:
        logging.warning("讀不到合併總資產總計的數值，略過每日快照")
        return state

    ws.update_acell(f"D{yesterday_row}", total_value)
    state["last_snapshot_date"] = today
    logging.info("每日快照：D%s（前一日總資產）更新為 %s", yesterday_row, total_value)
    return state


def check_once(ws, state: dict) -> dict:
    signals = find_signals(ws)
    changes = []
    new_state = {"last_snapshot_date": state.get("last_snapshot_date")}
    for key, (label, value) in signals.items():
        old = state.get(key, {}).get("value")
        new_state[key] = {"label": label, "value": value}
        if old is not None and old != value:
            changes.append(f"{label}\n{old}\n→ {value}")

    if changes:
        text = "🔔 017 股市訊號變動\n\n" + "\n\n".join(changes)
        send(text)
        logging.info("推播訊號變動：%s", changes)

    new_state = daily_snapshot(ws, new_state)
    save_state(new_state)
    return new_state


def main():
    ws = open_sheet(CREDS_FILE, SPREADSHEET_ID)
    state = load_state()
    logging.info("監控啟動，目前訊號：%s", state)
    while True:
        try:
            state = check_once(ws, state)
        except Exception:
            logging.exception("檢查訊號失敗")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
