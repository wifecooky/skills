#!/bin/bash
# Launch the re-signed WeChat copy, pointing its home at the real account container
# via CFFIXED_USER_HOME so it logs into the existing account.
WORK="$HOME/.wechat-read"
COPY="$WORK/WeChatDbg.app"
CONT="$HOME/Library/Containers/com.tencent.xinWeChat/Data"

[ -d "$COPY" ] || { echo "ERROR: run setup_wechat.sh first"; exit 1; }

echo "Stopping any running WeChat (including your normal one) ..."
pkill -9 -x WeChat 2>/dev/null
sleep 2

echo "Launching re-signed copy with CFFIXED_USER_HOME=$CONT ..."
CFFIXED_USER_HOME="$CONT" HOME="$CONT" "$COPY/Contents/MacOS/WeChat" >/tmp/wechat-read.log 2>&1 &

PID=""
for i in $(seq 1 8000); do PID=$(pgrep -x WeChat | head -1); [ -n "$PID" ] && break; done
echo "WeChat PID: ${PID:-<none>}"
echo
echo "NEXT (user action):"
echo "  1. If an 'Open WeChat' button / QR login shows, click / scan it."
echo "  2. Open the TARGET chat and SCROLL UP to load its history into memory."
echo "  3. Then continue with dump.sh + carve.py."
