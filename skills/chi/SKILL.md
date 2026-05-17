# /chi — 詹小奇週報產生器

整理本週 Claude Code 對話的工作摘要，產生視覺化封面圖，並自動建立 Notion Make Time 頁面。

## 觸發時機
- 使用者輸入 `/chi`
- 說「產週報」、「做週報」、「產彙報」、「週報」

---

## Step 1：萃取本週工作內容

**素材來源是這週的 Claude Code 對話**（你與使用者實際做了什麼、討論了什麼）。

1. 讀取 `~/.claude/history.jsonl`，過濾本週（最近 7 天）的記錄。
2. 從當前對話與歷史記錄中整理：
   - 主要完成的任務或專案（名稱 + 一句說明）
   - 五大工作項目的分佈（AI工具、內容、門診、行政、學習）
   - 三件值得記下的好事
   - 主要決策或重要進展
   - 一句代表這週氛圍的金句
3. 以條列清單輸出給使用者確認，詢問：
   > 「有沒有要補充或修正的？沒有就說無。」
4. 整合使用者回覆後繼續。

---

## Step 2：產封面圖

封面圖是這週工作的**文字視覺化摘要**，讓人一眼看清楚這週做了什麼。

### 2.1 填入 HTML 模板

1. 讀取模板：`900_Agent/workflows/assets/kairos-weekly-cover.html`
2. 將以下位置替換為實際數據（只改文字，不動 CSS）：

| 位置 | 填入內容 | 限制 |
|------|---------|------|
| `.badge-icon` | 日期範圍（如 `0512–0518`）| 短格式 |
| `.week-label` | 週次（如 `WEEK 20 · 2026`）| |
| `.main-title .line1` | 本週主題第一行 | ≤3 中文字 |
| `.main-title .line2` | 本週主題第二行 | ≤3 中文字 |
| `.sub-text` | 一句話說明這週的核心 | ≤15字/行 |
| 第1個 `.data-card` | 最重要指標（值 + 標籤）| |
| 第2個 `.data-card` | 第二指標 | |
| 第3個 `.data-card` | 第三指標 | |
| `.stat-row` 5個 `.stat-value` | 週次、AI工具、系統設定、內容、達成率 | |
| `.bar-chart` 5個 `.bar-item` | 五大項目名稱 + 相對百分比 + 數量 | |
| `.good-things` 3個 `.good-item` | 好事三件 | 各1行，精簡 |
| `.highlights` 的 `.highlight-item` | 主要事項 | 2-3行 |
| `.week-quote` | 本週金句 | 1行 |

3. 將填好的 HTML 寫入 `~/Downloads/kairos-weekly-cover-filled.html`

### 2.2 截圖

1. 用 `ToolSearch` 載入：`mcp__playwright__browser_resize`、`mcp__playwright__browser_navigate`、`mcp__playwright__browser_wait_for`、`mcp__playwright__browser_take_screenshot`
2. 啟動 HTTP server：
   ```bash
   cp ~/Downloads/kairos-weekly-cover-filled.html /tmp/kairos-filled.html
   python3 -m http.server 7788 --directory /tmp &
   sleep 1
   ```
3. 設定視窗為 **1920×1080**
4. 導航至 `http://localhost:7788/kairos-filled.html`，等待 2 秒
5. 截圖儲存至 `~/Downloads/chi-cover-MMDD.png`
6. 關閉 server：`pkill -f "python3 -m http.server 7788"`

---

## Step 3：發布至 Notion Make Time

1. 用 `ToolSearch` 載入 `mcp__claude_ai_Notion__notion-create-pages`
2. 在 **[CC] Make Time Database**（ID：`1f3440b0-388d-81c4-9a2f-cea7fc618def`）建立新頁面：
   - **標題**：`YYYY-MM-DD`（週報產生當天，格式與每日早報相同）
   - **內文**：
     ```
     ## 詹小奇每週工作匯報 — 第 W 週（MM/DD–MM/DD）

     ### 本週完成
     [條列清單，主要任務]

     ### 好事三件
     [三件好事]

     ### 主要事項
     [重要決策/進展]

     ### 本週金句
     「[金句]」

     ---
     封面圖：~/Downloads/chi-cover-MMDD.png
     ```
3. 建立成功後回傳頁面連結。

---

## Step 4：輸出結果

依序輸出：
1. **本週摘要**（條列清單）
2. **封面圖**（截圖路徑）
3. **Notion 頁面連結**
4. 詢問：「需要調整封面文案嗎？」

---

## 注意事項
- 不需要寫 FB 貼文，只需要結構化摘要
- 內容來源是真實對話，不捏造；不確定的數字標注「約」
- 封面主標每行嚴格 ≤3 中文字
- bar chart 百分比：各項目數 ÷ 最大值 × 100%
- Notion 標題格式與早報相同：`YYYY-MM-DD`
