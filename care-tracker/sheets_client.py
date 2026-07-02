import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# 欄位索引（0-based）
MAIN_COLS = {
    "medical_id":        0,
    "name":              1,
    "project":           2,
    "enrollment_date":   3,
    "last_visit":        4,
    "tracking_interval": 5,   # 追蹤間隔（天），手動填入
    "earliest_next":     6,   # 下次最早可回診日，bot 計算寫入
    "status":            7,
    "notes":             8,
    "last_updated":      9,
    "updated_by":        10,
}

RECORD_COLS = {
    "medical_id":   0,
    "name":         1,
    "project":      2,
    "visit_date":   3,
    "notes":        4,
    "recorded_at":  5,
    "recorded_by":  6,
}

STATUS_ACTIVE  = "追蹤中"
STATUS_NOSHOW  = "爽約-待聯繫"
STATUS_PAUSED  = "暫停追蹤"
STATUS_CLOSED  = "停案"


class SheetsClient:
    def __init__(self, credentials_file: str, spreadsheet_name: str):
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        gc = gspread.authorize(creds)
        ss = gc.open(spreadsheet_name)
        self.main  = ss.worksheet("個案總表")
        self.record = ss.worksheet("回診記錄")

    # ── 讀取 ──────────────────────────────────────
    def all_patients(self) -> list[dict]:
        rows = self.main.get_all_values()
        patients = []
        for i, row in enumerate(rows[1:], start=2):
            if not row or not row[0]:
                continue
            patients.append({
                "row":              i,
                "medical_id":       row[MAIN_COLS["medical_id"]],
                "name":             row[MAIN_COLS["name"]],
                "project":          row[MAIN_COLS["project"]],
                "enrollment_date":  _parse_date(row[MAIN_COLS["enrollment_date"]]),
                "last_visit":       _parse_date(row[MAIN_COLS["last_visit"]]),
                "tracking_interval": _parse_int(row[MAIN_COLS["tracking_interval"]]),
                "earliest_next":    _parse_date(row[MAIN_COLS["earliest_next"]]),
                "status":           row[MAIN_COLS["status"]],
                "notes":            row[MAIN_COLS["notes"]],
            })
        return patients

    def patient_visits(self, medical_id: str, project: str) -> list[date]:
        rows = self.record.get_all_values()
        visits = []
        for row in rows[1:]:
            if (row[RECORD_COLS["medical_id"]] == medical_id and
                    row[RECORD_COLS["project"]] == project):
                d = _parse_date(row[RECORD_COLS["visit_date"]])
                if d:
                    visits.append(d)
        return sorted(visits)

    # ── 寫入 ──────────────────────────────────────
    def update_patient(self, row: int, fields: dict, updated_by: str = "系統"):
        fields["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        fields["updated_by"]   = updated_by
        for field, value in fields.items():
            if field not in MAIN_COLS:
                continue
            col = MAIN_COLS[field] + 1
            if isinstance(value, (date, datetime)):
                value = value.strftime("%Y-%m-%d")
            self.main.update_cell(row, col, value or "")

    def add_visit(self, medical_id: str, name: str, project: str,
                  visit_date: date, notes: str = "", recorded_by: str = "系統"):
        self.record.append_row([
            medical_id,
            name,
            project,
            visit_date.strftime("%Y-%m-%d"),
            notes,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            recorded_by,
        ])

    def add_patient(self, data: dict, added_by: str = "系統"):
        row = [""] * len(MAIN_COLS)
        for field, col in MAIN_COLS.items():
            if field == "earliest_next":
                continue  # G 欄由公式自動計算，不寫入靜態值
            v = data.get(field, "")
            if isinstance(v, (date, datetime)):
                v = v.strftime("%Y-%m-%d")
            row[col] = v or ""
        if not row[MAIN_COLS["status"]]:
            row[MAIN_COLS["status"]] = STATUS_ACTIVE
        row[MAIN_COLS["last_updated"]] = datetime.now().strftime("%Y-%m-%d %H:%M")
        row[MAIN_COLS["updated_by"]]   = added_by

        # 新增後取得列號，寫入自動換算公式到 G 欄
        next_row = len(self.main.get_all_values()) + 1
        self.main.append_row(row, value_input_option="USER_ENTERED")
        col_g = MAIN_COLS["earliest_next"] + 1  # 1-based
        formula = f'=IF(AND(E{next_row}<>"",F{next_row}<>""),E{next_row}+F{next_row},"")'
        self.main.update_cell(next_row, col_g, formula)


def _parse_date(value: str):
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip())
    except (ValueError, AttributeError):
        return None


def _parse_int(value: str):
    if not value:
        return None
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None
