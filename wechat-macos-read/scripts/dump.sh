#!/bin/bash
# Attach lldb to WeChat and dump its heap memory (decrypted SQLite pages live here).
PID="${1:-$(pgrep -x WeChat | head -1)}"
OUT="${2:-$HOME/.wechat-read/dump.bin}"
DIR="$(cd "$(dirname "$0")" && pwd)"

[ -n "$PID" ] || { echo "ERROR: WeChat not running"; exit 1; }
echo "Dumping memory of PID $PID -> $OUT (this takes ~1-2 min) ..."
rm -f "$OUT"
lldb -p "$PID" \
  -o "command script import $DIR/dumpmem.py" \
  -o "dumpmem $OUT" \
  -o "detach" -o "quit" 2>&1 | grep -E 'DUMPED_REGIONS|error|no such' || true
[ -s "$OUT" ] && echo "OK: $(ls -lh "$OUT" | awk '{print $5}') -> $OUT" || echo "FAILED (empty dump)"
