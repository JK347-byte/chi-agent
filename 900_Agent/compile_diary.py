#!/usr/bin/env python3
"""
006 日記自動整理 — 每晚 00:00 執行
資料來源：Inbox 筆記、Chrome 瀏覽紀錄、Git log
"""

import os
import sqlite3
import shutil
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

import anthropic

VAULT = Path("/Users/janskey/Documents/Obsidian Vault/NumbersOffice")
DIARY_PATH = VAULT / "006_Diary/diary_2026.md"
INBOX_PATH = VAULT / "006_Diary/inbox"
CHROME_HISTORY = Path.home() / "Library/Application Support/Google/Chrome/Default/History"
CHI_AGENT = Path("/Users/janskey/Downloads/Chi-Agent")
LOG_PATH = CHI_AGENT / "900_Agent/diary_bot.log"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def get_chrome_history(target_date):
    if not CHROME_HISTORY.exists():
        return []
    tmp = Path("/tmp/chrome_history_diary_copy")
    try:
        shutil.copy2(CHROME_HISTORY, tmp)
        conn = sqlite3.connect(tmp)
        # Chrome timestamps: microseconds since 1601-01-01
        epoch_start = datetime(1601, 1, 1)
        day_start = datetime(target_date.year, target_date.month, target_date.day)
        day_end = day_start + timedelta(days=1)
        chrome_start = int((day_start - epoch_start).total_seconds() * 1_000_000)
        chrome_end = int((day_end - epoch_start).total_seconds() * 1_000_000)
        rows = conn.execute("""
            SELECT url, title, visit_count
            FROM urls
            WHERE last_visit_time BETWEEN ? AND ?
            ORDER BY last_visit_time DESC
            LIMIT 60
        """, (chrome_start, chrome_end)).fetchall()
        conn.close()
        return rows
    except Exception as e:
        log(f"Chrome history 讀取失敗: {e}")
        return []
    finally:
        tmp.unlink(missing_ok=True)


def get_inbox_notes(target_date):
    notes = []
    date_str = target_date.strftime("%Y-%m-%d")
    for f in sorted(INBOX_PATH.glob("*.md")):
        if f.name == "README.md":
            continue
        text = f.read_text(encoding="utf-8")
        if date_str in text or date_str in f.name:
            notes.append((f.name, text))
    return notes


def get_all_unprocessed_inbox():
    """抓取所有尚未處理的 inbox 筆記（補日記用）"""
    notes = []
    for f in sorted(INBOX_PATH.glob("*.md")):
        if f.name == "README.md":
            continue
        notes.append((f.name, f.read_text(encoding="utf-8")))
    return notes


def get_git_log(target_date):
    date_str = target_date.strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log",
             f"--after={date_str} 00:00",
             f"--before={date_str} 23:59:59",
             "--oneline", "--all"],
            cwd=CHI_AGENT, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        log(f"Git log 讀取失敗: {e}")
        return ""


def diary_exists(target_date):
    date_str = target_date.strftime("%Y-%m-%d")
    try:
        return f"## {date_str}" in DIARY_PATH.read_text(encoding="utf-8")
    except Exception:
        return False


def write_diary(entry, target_date):
    with open(DIARY_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + entry.strip() + "\n")
    log(f"✓ 已寫入 {target_date.strftime('%Y-%m-%d')}")


def clear_inbox_files(filenames):
    for name in filenames:
        path = INBOX_PATH / name
        if path.exists() and name != "README.md":
            path.unlink()
            log(f"✓ 清除 inbox: {name}")


def compile_diary_for(target_date):
    date_str = target_date.strftime("%Y-%m-%d")

    if diary_exists(target_date):
        log(f"日記 {date_str} 已存在，跳過")
        return

    log(f"開始整理 {date_str} 的日記...")

    chrome = get_chrome_history(target_date)
    inbox = get_inbox_notes(target_date)
    gitlog = get_git_log(target_date)

    chrome_text = "\n".join(
        [f"- {title or url}" for url, title, _ in chrome if title][:40]
    ) or "（無紀錄）"

    inbox_text = "\n\n".join(
        [f"【{name}】\n{content}" for name, content in inbox]
    ) or "（無筆記）"

    gitlog_text = gitlog or "（無提交）"

    prompt = f"""你是 006 日記助理，以第三人稱觀察者視角，記錄詹士奇的一天。

## 整理日期
{date_str}

## 資料來源

### Inbox 筆記（Telegram 手動輸入）
{inbox_text}

### Chrome 瀏覽紀錄
{chrome_text}

### Claude Code Git 提交記錄
{gitlog_text}

## 輸出規則
- 嚴格按照格式輸出，不加任何前言或後記
- 全程第三人稱（詹士奇、他、醫師）
- 不用「我」「你」
- 語氣冷靜、有觀察距離，偶爾點出行為背後的模式
- 繁體中文，文字簡練
- 三個資料來源都要整合，但不要逐條列出所有瀏覽網址，要歸納成有意義的行為描述

## 輸出格式
## {date_str}（觀察日誌）
[開場：當天氛圍一句話]

**[段落標題1]**
- 條列重點

**[段落標題2]**
- 條列重點

---

[收尾：觀察者視角的一段話，點出這一天的隱含脈絡]"""

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    entry = response.content[0].text
    write_diary(entry, target_date)

    # 清除已處理的 inbox 檔案
    clear_inbox_files([name for name, _ in inbox])


def main():
    yesterday = date.today() - timedelta(days=1)
    log(f"=== 006 日記整理啟動，目標日期：{yesterday} ===")
    compile_diary_for(yesterday)
    log("=== 完成 ===")


if __name__ == "__main__":
    main()
