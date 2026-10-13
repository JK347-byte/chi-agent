#!/bin/bash
# 檢查 017 的兩支背景程式是否還在跑，沒有的話就重新啟動
cd /Users/janskey/Downloads/Chi-Agent/017_Stock || exit 1

if ! pgrep -f "monitor\.py$" > /dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') 偵測到訊號監控沒在跑，重新啟動" >> watchdog.log
    nohup /usr/bin/python3 monitor.py >> monitor_run.log 2>&1 &
    disown
fi

if ! pgrep -f "inbox_bot\.py$" > /dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') 偵測到訊息收集bot沒在跑，重新啟動" >> watchdog.log
    nohup /usr/bin/python3 inbox_bot.py >> inbox_bot_run.log 2>&1 &
    disown
fi
