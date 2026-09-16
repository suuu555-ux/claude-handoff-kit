#!/bin/bash
# handoff plugin 狀態列：模型 · 專案 · context 用量五格量表 · git 分支
# 用量跨過 THRESHOLD（預設 40%）時跳一次 macOS 通知，提醒跑 /handoff:last-word 收工再 /clear。
# 只在「由低往上跨線」那一刻通知（每個 session 一次；壓縮後降回再升會再通知，是刻意的）。
# 依賴：bash、python3（macOS 內建）。不需要 jq。

THRESHOLD="${HANDOFF_THRESHOLD:-40}"
input=$(cat)

# 用 python3 解析 Claude Code 餵進來的 JSON（一次取四個欄位）
read -r pct model dir sid < <(printf '%s' "$input" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
cw = d.get("context_window") or {}
pct = cw.get("used_percentage") or 0
m = d.get("model") or {}
model = m.get("display_name") or m.get("id") or "claude"
ws = d.get("workspace") or {}
dr = ws.get("current_dir") or d.get("cwd") or "."
sid = d.get("session_id") or "default"
# 空白會弄壞 read，統一換成底線
print(int(float(pct)), model.replace(" ", "_"), dr.replace(" ", "_"), sid)
')
[ -z "$pct" ] && pct=0
base=$(basename "$dir")

# ---- 五格量表 ----
filled=$(( pct / 20 )); [ "$filled" -gt 5 ] && filled=5
bar=""
for i in 1 2 3 4 5; do
  if [ "$i" -le "$filled" ]; then bar="${bar}▮"; else bar="${bar}▯"; fi
done

# ---- 顏色 ----
RED=$'\033[31m'; YEL=$'\033[33m'; DIM=$'\033[2m'; MAG=$'\033[35m'; RST=$'\033[0m'
if   [ "$pct" -ge "$THRESHOLD" ]; then col="$RED"; mark="*"
elif [ "$pct" -ge 25 ];          then col="$YEL"; mark=""
else col="$DIM"; mark=""; fi

# ---- 跨線偵測 → 每次由低往上跨線通知一次 ----
markdir="$HOME/.claude/.handoff-markers"
mkdir -p "$markdir" 2>/dev/null
state="$markdir/$(printf '%s' "$sid" | tr -cd 'A-Za-z0-9_-')"
prev=0; [ -f "$state" ] && prev=$(cat "$state" 2>/dev/null)
prev=${prev%.*}; [ -z "$prev" ] && prev=0
if [ "$pct" -ge "$THRESHOLD" ] && [ "$prev" -lt "$THRESHOLD" ]; then
  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"對話容量已用 ${pct}%，先跑 /handoff:last-word 收工再 /clear\" with title \"該收工了\" sound name \"Glass\"" >/dev/null 2>&1 &
  fi
fi
printf '%s' "$pct" > "$state"

printf '%s%s · %s%s · %s%s %s%%%s%s' \
  "$DIM" "${model//_/ }" "$base" "$RST" \
  "$col" "$bar" "$pct" "$mark" "$RST"

# ---- git 分支＋未提交星號（2 秒逾時，避免大 repo 卡住狀態列）----
if [ -n "$dir" ] && [ -d "$dir" ]; then
  git_raw=$(
    (
      if git -C "$dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        b=$(git -C "$dir" branch --show-current 2>/dev/null)
        [ -z "$b" ] && b=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
        d=""; [ -n "$(git -C "$dir" status --porcelain -uno 2>/dev/null | head -1)" ] && d="*"
        printf '%s|%s' "$b" "$d"
      fi
    ) &
    _gp=$!
    ( sleep 2; kill -9 "$_gp" 2>/dev/null ) >/dev/null 2>&1 &
    _wp=$!
    wait "$_gp" 2>/dev/null
    kill -9 "$_wp" 2>/dev/null; wait "$_wp" 2>/dev/null
  )
  gb=$(printf '%s' "$git_raw" | cut -d'|' -f1)
  gd=$(printf '%s' "$git_raw" | cut -d'|' -f2)
  [ -n "$gb" ] && printf ' · %s⎇ %s%s%s%s%s' "$MAG" "$gb" "$RST" "$RED" "$gd" "$RST"
fi

exit 0
