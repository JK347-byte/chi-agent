# /morning — 手動觸發每日早報

立即執行「每日早報 — Make Time」routine，在 Notion [CC] Make Time Database 建立或更新今日頁面。

## 觸發時機
- 使用者輸入 `/morning`
- 使用者說「執行早報」、「觸發早報」、「跑早報」、「幫我產今天的早報」

## 執行步驟

1. 使用 `ToolSearch` 載入 `RemoteTrigger` 工具（若尚未載入）
2. 呼叫 `RemoteTrigger`：
   ```json
   {
     "action": "run",
     "trigger_id": "trig_01VGZ4sduD2A68aAojMKE8eY"
   }
   ```
3. 回報結果給使用者：
   - 成功：「✅ 早報已觸發，約 1–2 分鐘後可在 Notion Make Time 頁面查看今日早報。」
   - 失敗：顯示錯誤訊息並建議前往 https://claude.ai/code/routines 確認狀態

## 注意事項
- 此 routine 同時設有每日 05:30（台北時間）自動排程，手動觸發不影響自動排程
- Routine ID：`trig_01VGZ4sduD2A68aAojMKE8eY`
- 連結：https://claude.ai/code/routines/trig_01VGZ4sduD2A68aAojMKE8eY
