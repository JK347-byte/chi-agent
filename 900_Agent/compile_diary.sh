#!/bin/bash
# 006 日記自動整理 — 每晚 00:00 執行
# 資料來源：Inbox 筆記、Chrome 瀏覽紀錄、Git log

VAULT="/Users/janskey/Documents/Obsidian Vault/NumbersOffice"
DIARY="$VAULT/006_Diary/diary_2026.md"
INBOX="$VAULT/006_Diary/inbox"
CHROME_DB="$HOME/Library/Application Support/Google/Chrome/Default/History"
CHI_AGENT="/Users/janskey/Downloads/Chi-Agent"
LOG="$CHI_AGENT/900_Agent/diary_bot.log"
CLAUDE="/Applications/cmux.app/Contents/Resources/bin/claude"

# 目標日期：昨天，或傳入第一個參數
if [ -n "$1" ]; then
  YESTERDAY="$1"
  DATE_COMPACT=$(echo "$1" | tr -d '-')
else
  YESTERDAY=$(date -v-1d +%Y-%m-%d)
  DATE_COMPACT=$(date -v-1d +%Y%m%d)
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"; }

log "=== 006 日記整理啟動，目標日期：$YESTERDAY ==="

# 檢查日記是否已存在
if grep -q "## $YESTERDAY" "$DIARY" 2>/dev/null; then
  log "日記 $YESTERDAY 已存在，跳過"
  exit 0
fi

# ── 1. Inbox 筆記 ──────────────────────────────────────────────
INBOX_TEXT=""
for f in "$INBOX"/*.md; do
  fname=$(basename "$f")
  [ "$fname" = "README.md" ] && continue
  if grep -q "$YESTERDAY" "$f" 2>/dev/null || echo "$fname" | grep -q "$DATE_COMPACT"; then
    INBOX_TEXT="$INBOX_TEXT\n【$fname】\n$(cat "$f")\n"
  fi
done
[ -z "$INBOX_TEXT" ] && INBOX_TEXT="（無筆記）"

# ── 2. Chrome 瀏覽紀錄 ─────────────────────────────────────────
CHROME_TEXT="（無紀錄）"
if [ -f "$CHROME_DB" ]; then
  TMP_DB="/tmp/chrome_diary_$DATE_COMPACT.db"
  cp "$CHROME_DB" "$TMP_DB" 2>/dev/null
  if [ -f "$TMP_DB" ]; then
    # Chrome timestamp = microseconds since 1601-01-01; 11644473600 seconds offset from Unix epoch
    CHROME_TEXT=$(sqlite3 "$TMP_DB" "
      SELECT title
      FROM urls
      WHERE last_visit_time >= (strftime('%s','$YESTERDAY') + 11644473600) * 1000000
        AND last_visit_time <  (strftime('%s','$YESTERDAY') + 11644473600 + 86400) * 1000000
        AND title != ''
      ORDER BY last_visit_time DESC
      LIMIT 50;
    " 2>/dev/null | head -50)
    rm -f "$TMP_DB"
    [ -z "$CHROME_TEXT" ] && CHROME_TEXT="（無紀錄）"
  fi
fi

# ── 3. Git log ─────────────────────────────────────────────────
GIT_LOG=$(git -C "$CHI_AGENT" log \
  --after="$YESTERDAY 00:00" \
  --before="$YESTERDAY 23:59:59" \
  --oneline --all 2>/dev/null)
[ -z "$GIT_LOG" ] && GIT_LOG="（無提交）"

# ── 4. 組合 prompt 並呼叫 Claude CLI ──────────────────────────
PROMPT="你是 006 日記助理，以第三人稱觀察者視角，記錄詹士奇的一天。

## 整理日期
$YESTERDAY

## 資料來源

### Inbox 筆記（Telegram 手動輸入）
$INBOX_TEXT

### Chrome 瀏覽紀錄（頁面標題）
$CHROME_TEXT

### Claude Code Git 提交記錄
$GIT_LOG

## 輸出規則
- 只輸出日記正文，不加任何前言、後記、說明、警告或評論
- 不要輸出「已輸出」「請確認」「無法寫入」等系統說明文字
- 全程第三人稱（詹士奇、他、醫師）
- 不用「我」「你」
- 繁體中文

## 寫作要求（重要）
這不是活動清單，是觀察者的文學筆記。

**不要做的事：**
- 不要條列事件（「搜尋了A、開啟了B、完成了C」）
- 不要逐項列出瀏覽記錄
- 不要只描述「做了什麼」

**要做的事：**
- 從行為推斷狀態：他為什麼反覆搜尋同一個詞？那個動作背後是焦慮、習慣、還是猶豫？
- 把瀏覽痕跡讀成一種心理地圖：這天他的注意力流向哪裡，說明了什麼？
- 捕捉節奏感：這天是快的、慢的、散的、收斂的？
- 如果有家庭記錄（inbox 筆記），要特別細寫，這是最私人的部分
- 讓每個段落都有「觀點」，不只是描述，而是解讀

**參考語氣：**
冷靜、有距離，但不冷漠。像一個認識他很久的旁觀者，看出他自己沒說出口的東西。

## 輸出格式（嚴格遵守，直接輸出以下結構）

## $YESTERDAY [主題標題]
（主題標題：3–6 字，捕捉當天最核心的事件或氛圍）

### 一、事實

**手寫備注（Inbox）**
（若有 Inbox 筆記，以列點逐條呈現，保留原文語氣與時間戳記。若無則寫「（本日無備注）」）

**數位足跡**
（記錄瀏覽行為與 Claude 工作。排版規則：
- 同一類行為用列點；不同性質的事件另起一段
- 遇到工具名稱、地名、人名、醫學術語等，加一句簡短說明，讓不熟悉的人也能看懂
- 目標 200–250 字）

---

### 二、抽象化思考

（從事實中提煉洞察，優先用 Why 型：他為什麼這樣做？背後的動機或慣性是什麼？
遇到有趣的行為模式，多停留一句，把它說透。目標 150–200 字。）

### 三、轉化應用

（這一天的觀察，指向最重要的 1–2 個行動或提醒。
不同主題分段；同主題用段落，不用列點。目標 80–120 字。）

---"

log "呼叫 Claude 整理日記..."
RAW=$(echo "$PROMPT" | "$CLAUDE" -p --output-format text 2>/dev/null)

# 只保留從 ## 20XX 開頭的日記本文，移除 Claude 的說明文字
ENTRY=$(echo "$RAW" | sed -n '/^## 20/,$p' | grep -v "條目已就緒\|日記正文已顯示\|檔案寫入\|請授權\|無法寫入\|寫入權限")

if [ -z "$ENTRY" ]; then
  log "Claude 回應為空或格式異常，整理失敗"
  log "原始回應：$RAW"
  exit 1
fi

# ── 5. 前置寫入日記（最新在最上方）──────────────────────────────
TEMP=$(mktemp)
printf '%s\n\n' "$ENTRY" > "$TEMP"
cat "$DIARY" >> "$TEMP"
mv "$TEMP" "$DIARY"
log "✓ 已寫入 $YESTERDAY（置頂）"

# ── 6. 清除已處理的 inbox 檔案 ────────────────────────────────
for f in "$INBOX"/*.md; do
  fname=$(basename "$f")
  [ "$fname" = "README.md" ] && continue
  if grep -q "$YESTERDAY" "$f" 2>/dev/null || echo "$fname" | grep -q "$DATE_COMPACT"; then
    rm "$f"
    log "✓ 清除 inbox: $fname"
  fi
done

log "=== 完成 ==="
