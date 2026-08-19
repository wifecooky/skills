#!/bin/bash
# Copy WeChat.app and ad-hoc re-sign it (strip hardened runtime) so lldb can attach
# WITHOUT disabling SIP. Original /Applications/WeChat.app is never touched.
set -e
APP_SRC="/Applications/WeChat.app"
WORK="$HOME/.wechat-read"
COPY="$WORK/WeChatDbg.app"
CONT="$HOME/Library/Containers/com.tencent.xinWeChat/Data"

[ -d "$APP_SRC" ] || { echo "ERROR: $APP_SRC not found (is WeChat installed?)"; exit 1; }
[ -d "$CONT/Documents/xwechat_files" ] || { echo "ERROR: not WeChat 4.x (no xwechat_files under container)"; exit 1; }

mkdir -p "$WORK"
echo "[1/3] Copying WeChat.app -> $COPY ..."
rm -rf "$COPY"
ditto "$APP_SRC" "$COPY"

echo "[2/3] Ad-hoc re-signing (removes hardened runtime; keeps app runnable) ..."
codesign --force --deep --sign - "$COPY"
codesign -v "$COPY" && echo "    signature verified OK"

echo "[3/3] Account data dir(s):"
ls -d "$CONT/Documents/xwechat_files"/wxid_* 2>/dev/null | sed 's/^/    /'
echo "    CFFIXED_USER_HOME will be: $CONT"
echo "Setup done."
