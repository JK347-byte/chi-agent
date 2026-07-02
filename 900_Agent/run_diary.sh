#!/bin/bash
# 006 日記自動整理 — wrapper script

# 載入環境變數
source ~/.zshrc 2>/dev/null || source ~/.bash_profile 2>/dev/null || true

# 如果環境中沒有 API key，從檔案載入
if [ -z "$ANTHROPIC_API_KEY" ]; then
  KEYFILE="$HOME/.claude/anthropic_api_key"
  if [ -f "$KEYFILE" ]; then
    export ANTHROPIC_API_KEY=$(cat "$KEYFILE")
  fi
fi

cd /Users/janskey/Downloads/Chi-Agent
/usr/bin/python3 /Users/janskey/Downloads/Chi-Agent/900_Agent/compile_diary.py
