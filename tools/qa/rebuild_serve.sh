#!/usr/bin/env bash
# Rebuild dist and (re)start a local static server on :8091 (Windows Git Bash friendly).
cd "$(dirname "$0")/../.."
PID=$(netstat -ano 2>/dev/null | grep ":8091 " | grep LISTENING | awk '{print $5}' | head -1)
[ -n "$PID" ] && taskkill //F //PID "$PID" >/dev/null 2>&1
sleep 1
PYTHONUTF8=1 python build.py | tail -1
cd dist && (nohup python -m http.server 8091 >/tmp/llfserve.log 2>&1 &)
sleep 2
