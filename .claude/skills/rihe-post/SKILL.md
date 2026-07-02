---
name: rihe-post
description: >
  日和聯合診所醫療衛教內容創作工具。使用者提供文章主題、副標、三個重點後，
  自動搜尋最新醫學文獻、撰寫去 AI 化的 Facebook 貼文，生成 1200x1200 封面圖，
  並生成 1200x1200 資訊圖表（自動選擇迷思 vs 事實 / 重點整理卡 / 步驟流程三種版型）。
  觸發時機：使用者提供文章構想（主題、副標、重點）；說「幫我寫文章」「做封面」
  「衛教文章」「FB 貼文」；以及任何耳鼻喉科 / 家醫科 / 小兒科的內容創作需求。
---

# 日和聯合診所 內容創作 Studio

## 診所基本資料

- **診所**：日和聯合診所（台南市鹽水區）
- **醫師**：詹士奇醫師（耳鼻喉科 / 家醫科 / 小兒科）
- **預約專線**：06-6520182
- **固定 hashtag**：每篇必帶 `#日和聯合診所` `#詹士奇醫師`

---

## 執行流程

使用者提供 **主題 + 副標 + 三個重點** 後，依序執行以下五步。

---

### Step 1｜搜尋醫學文獻

用 WebSearch 針對主題搜尋一次（中文為主）：
- 搜尋詞：`[主題] 台灣耳鼻喉科` 或 `[主題] 衛福部 疾管署 2024 2025`
- 目標：找 2–3 個具體數據（發生率、治癒率、研究數字）或最新臨床建議
- 整理成筆記備用，後續自然帶入文章

---

### Step 2｜撰寫 FB 貼文

#### 語氣原則
專業但親切，像在跟朋友解釋。不說教，不堆術語，有溫度。

#### 文體選擇
依主題選擇最適合的文體，範本在 `references/post-templates.md`：

| 類型 | 適用場合 |
|------|---------|
| A 迷思破解 | 反直覺題材，分享率最高 |
| B 季節提醒 | 疾管署警報、換季 |
| C 公衛警示 | 腸病毒 / RSV / 流感 |
| D 學術新知 | 期刊研究轉譯 |
| E 數據震撼 | 三高 / 慢性病盛行率 |

#### FB 格式規範（嚴格遵守）

| 元素 | 符號 | 說明 |
|------|------|------|
| 開頭標題 | `【標題】` | 第一行，單獨一行，後面不加副標 |
| 段落主標 | `▋ 標題` | 各大段落 |
| 段落小標 | `▍ 小標` | 段落內子分類 |
| 條列（無順序）| `● 項目` | 一律實心圓，禁止數字列點 |
| 步驟（有順序）| `1️⃣ 2️⃣ 3️⃣` | 僅限有明確先後順序時使用 |

#### Humanizer 去 AI 化（應用於段落正文）

完整 24 條規則見 `references/humanizer-rules.md`。

**寫作時優先過濾這幾條：**
- 禁用高頻 AI 詞：此外、至關重要、深入探討、格局、賦能、彰顯、寶貴、充滿活力
- 不用「挑戰與未來展望」公式結尾
- 不用否定排比（「不是 A，而是 B；不是 C，而是 D」）
- 結尾要具體，不寫通用正面結論
- 適度第一人稱（「在門診常遇到…」「我有時候跟患者說…」）
- 長短句交替，製造自然節奏

> FB 格式符號（▋ ▍ ● 1️⃣2️⃣3️⃣ 📌🎯📊）是結構元素，不受 Humanizer emoji 禁用限制。

#### 輸出格式

```
📌 選題：[題目]
🎯 目標受眾：[描述]
📊 預測互動：[分享型 / 留言型 / 儲存型]

--- 貼文內文（直接可貼 FB）---

[完整貼文]

本文資訊僅供衛教參考，不取代專業醫療診斷與治療建議。如有症狀請諮詢醫師。

🔖 來源引用：[論文或指引，含年份]
#主題tag #日和聯合診所 #詹士奇醫師

--- 內部備註（審閱後刪除）---
⚠️ 建議醫師確認：[需確認的醫學細節]
💡 延伸發展：[後續可延伸的方向]
```

#### 貼文結尾固定四層

```
▋ 詹醫師的溫馨提醒
[叮嚀內文]

專業檢查與諮詢：請洽「日和聯合診所」
讓我們把關你的健康。
預約專線：06-6520182

本文資訊僅供衛教參考，不取代專業醫療診斷與治療建議。如有症狀請諮詢醫師。

🔖 來源引用：[來源]
#tag1 #tag2 #日和聯合診所 #詹士奇醫師
```

#### 醫療法規禁止事項
- 具體藥品劑量推薦
- 「保證治癒」「一定有效」等絕對說法
- 未經確認的偏方背書
- 可辨識特定病患的描述

---

### Step 3｜更新封面 HTML

模板：`/Users/janskey/Downloads/Chi-Agent/cover_demo.html`
圖片：`/Users/janskey/Downloads/Chi-Agent/assets/photos/`

更新以下欄位（只改文字內容，不動 CSS）：

| HTML 元素 | 填入內容 |
|-----------|---------|
| `.category-tag` | 文章分類（例：耳鼻喉健康知識） |
| `.article-title` | 標題，`<br>` 在自然斷句處分兩行 |
| `.article-subtitle` | 核心主張一句話，簡短有力 |
| 三個 `.stat-num` | 三個統計數字，含 `<span class="stat-unit">` 單位 |
| 三個 `.stat-desc` | 每個數字的說明，15–20 字 |
| 三個 `.key-point span` | 每張卡片的行動建議，各 15–20 字 |

封面為純文字設計，無形象照，不需選擇或更換照片。

---

### Step 4｜截圖輸出

確認伺服器（port 8765）：
```bash
lsof -i :8765 | grep LISTEN
# 若無：cd /Users/janskey/Downloads/Chi-Agent && python3 -m http.server 8765 &
```

Playwright 截圖：
- 視窗：1200 × 1200
- 網址：`http://localhost:8765/cover_demo.html`
- 輸出：`/Users/janskey/Downloads/Chi-Agent/cover_output.jpeg`

截圖後讀取圖片顯示給使用者確認。

---

### Step 5｜資訊圖表截圖

模板：`/Users/janskey/Downloads/Chi-Agent/infographic.html`

#### 版型選擇邏輯

根據文章內容選擇最適合的版型，每次只顯示一種（其餘用 `style="display:none"` 隱藏）：

| 版型 | 顯示區塊 | 適用場合 |
|------|---------|---------|
| A 迷思 vs 事實 | `#section-myth-fact` | 文章主旨是破解常見錯誤觀念 |
| B 重點整理卡 | `#section-keypoints` | 文章提供清楚的三個知識重點 |
| C 步驟流程 | `#section-steps` | 文章描述治療流程或行動順序 |

#### 各版型需更新的 HTML 元素

**通用欄位（三種版型都要更新）：**

| 元素 | 填入內容 |
|------|---------|
| `#category-pill` | 分類（例：耳鼻喉健康知識） |
| `#type-label` | 版型說明（迷思 VS 事實 / 重點整理 / 步驟流程） |
| `#main-title` | 資訊圖表標題，和封面標題可以不同，更直接一點 |

**版型 A 迷思 vs 事實（共 12 個欄位）：**

| 元素 | 說明 |
|------|------|
| `#myth-1` / `#myth-1-sub` | 迷思一主文 / 補充說明 |
| `#myth-2` / `#myth-2-sub` | 迷思二主文 / 補充說明 |
| `#myth-3` / `#myth-3-sub` | 迷思三主文 / 補充說明 |
| `#fact-1` / `#fact-1-sub` | 事實一主文 / 補充說明 |
| `#fact-2` / `#fact-2-sub` | 事實二主文 / 補充說明 |
| `#fact-3` / `#fact-3-sub` | 事實三主文 / 補充說明 |

迷思主文簡短有力（10–15 字），sub 補充一般人會這樣想的理由（15–20 字）。
事實主文是正確觀念，sub 是簡短機制說明。

**版型 B 重點整理卡：**

| 元素 | 說明 |
|------|------|
| `#kp-title-1` / `#kp-desc-1` | 重點一標題 / 說明 |
| `#kp-title-2` / `#kp-desc-2` | 重點二標題 / 說明 |
| `#kp-title-3` / `#kp-desc-3` | 重點三標題 / 說明 |

**版型 C 步驟流程：**

| 元素 | 說明 |
|------|------|
| `#step-title-1` / `#step-desc-1` | 步驟一標題 / 說明 |
| `#step-title-2` / `#step-desc-2` | 步驟二標題 / 說明 |
| `#step-title-3` / `#step-desc-3` | 步驟三標題 / 說明 |

#### Playwright 截圖

- 視窗：1200 × 1200
- 網址：`http://localhost:8765/infographic.html`
- 輸出：`/Users/janskey/Downloads/Chi-Agent/infographic_output.jpeg`

截圖後讀取圖片顯示給使用者確認。

---

### Step 6｜存檔至 009_Social

貼文產出並確認後，依序執行三個動作：

#### 6-1｜複製圖片至 assets

```bash
cp /Users/janskey/Downloads/Chi-Agent/cover_output.jpeg \
   "/Users/janskey/Documents/Obsidian Vault/NumbersOffice/009_Social/assets/YYYY-MM-DD_主題_cover.jpeg"

cp /Users/janskey/Downloads/Chi-Agent/infographic_output.jpeg \
   "/Users/janskey/Documents/Obsidian Vault/NumbersOffice/009_Social/assets/YYYY-MM-DD_主題_infographic.jpeg"
```

#### 6-2｜建立貼文 markdown

- **路徑**：`/Users/janskey/Documents/Obsidian Vault/NumbersOffice/009_Social/posts/`
- **檔名**：`YYYY-MM-DD_主標題_副標題.md`
- **內容結構**：

```
# [標題]

## 視覺素材

![[YYYY-MM-DD_主題_cover.jpeg]]
![[YYYY-MM-DD_主題_infographic.jpeg]]

---

[完整貼文正文，含 hashtag，不含內部備註]
```

#### 6-3｜回報完成

```
✅ 已存入 009_Social/posts/YYYY-MM-DD_主題.md
✅ 封面圖、資訊圖表已複製至 009_Social/assets/
```

---

## 品質 Checklist

- [ ] 有 📌🎯📊 三行 meta
- [ ] 格式符合（`【】` `▋` `▍` `●` 或 `1️⃣2️⃣3️⃣`，無數字列點）
- [ ] 有「詹醫師的溫馨提醒」
- [ ] 有就診呼籲 + 電話
- [ ] 免責聲明在 hashtag 前
- [ ] 🔖 來源引用已填
- [ ] 含 `#日和聯合診所` `#詹士奇醫師`
- [ ] 有 ⚠️ 醫師確認 + 💡 延伸發展備註
- [ ] 字數 200–400 字
- [ ] 無絕對性療效聲明
- [ ] 無高頻 AI 詞
- [ ] 資訊圖表版型選擇合理（A/B/C）
- [ ] infographic.html 三個版型只顯示一個
- [ ] 資訊圖表截圖已輸出 `infographic_output.jpeg`
- [ ] 封面圖已複製至 `009_Social/assets/YYYY-MM-DD_主題_cover.jpeg`
- [ ] 資訊圖表已複製至 `009_Social/assets/YYYY-MM-DD_主題_infographic.jpeg`
- [ ] markdown 內含 `![[cover]]` 與 `![[infographic]]` 圖片連結
