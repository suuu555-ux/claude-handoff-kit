#!/bin/bash
# handoff 收工交接工具 安裝／移除腳本
#
# 安裝：   curl -fsSL https://raw.githubusercontent.com/suuu555-ux/claude-handoff-kit/main/install.sh | bash
# 移除：   bash ~/.claude/scripts/handoff/install.sh --uninstall
# 強制換狀態列：bash ~/.claude/scripts/handoff/install.sh --force-statusline
#
# 裝到哪：
#   ~/.claude/commands/last-word.md、pickup.md   → 指令 /last-word、/pickup
#   ~/.claude/scripts/handoff/*.py、statusline.sh  → 指令用的小腳本＋狀態列
#   ~/.claude/settings.json 的 statusLine        → 只在原本沒設定時寫入（有就不碰，印提示）
set -u

RAW="${HANDOFF_KIT_SRC:-https://raw.githubusercontent.com/suuu555-ux/claude-handoff-kit/main}"
CLAUDE="$HOME/.claude"
CMD="$CLAUDE/commands"
SCR="$CLAUDE/scripts/handoff"
SETTINGS="$CLAUDE/settings.json"
FILES_CMD="last-word.md pickup.md"
FILES_SCR="handoff-scope.py session-prune.py statusline.sh install.sh"

fetch() {  # fetch <相對路徑> <目的檔>
  if [ -d "$RAW" ]; then cp "$RAW/$1" "$2"; else curl -fsSL "$RAW/$1" -o "$2"; fi
}

uninstall() {
  for f in $FILES_CMD; do rm -f "$CMD/$f"; done
  rm -rf "$SCR"
  "${PY:-python3}" - "$SETTINGS" <<'PY'
import json, os, sys
p = sys.argv[1]
if os.path.exists(p):
    s = json.load(open(p))
    c = (s.get("statusLine") or {}).get("command", "")
    if "scripts/handoff/statusline.sh" in c:
        del s["statusLine"]
        json.dump(s, open(p, "w"), ensure_ascii=False, indent=2)
        print("已移除 settings.json 的 statusLine")
PY
  echo "✅ handoff 已移除（交接單 ~/.claude/handoffs/ 保留，要清自己刪）"
}

case "${1:-}" in
  --uninstall) uninstall; exit 0 ;;
esac

# 找 python：Windows 通常只有 python，且要確認不是 Microsoft Store 那個假捷徑
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -z "$PY" ] && { echo "❌ 找不到 Python 3.8+。Windows 請到 python.org 安裝並勾選「Add python.exe to PATH」，裝完重開終端機再跑一次。"; exit 1; }
case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) echo "ℹ 偵測到 Windows（Git Bash）：通知走 PowerShell toast；狀態列與指令行為未在 Windows 實測過，遇到問題請把錯誤原文貼給 Claude" ;;
esac

mkdir -p "$CMD" "$SCR" || { echo "❌ 建不了 $CLAUDE 目錄"; exit 1; }
for f in $FILES_CMD; do fetch "commands/$f" "$CMD/$f" || { echo "❌ 下載失敗：commands/$f"; exit 1; }; done
for f in $FILES_SCR; do
  src="scripts/$f"; [ "$f" = "install.sh" ] && src="install.sh"
  fetch "$src" "$SCR/$f" || { echo "❌ 下載失敗：$src"; exit 1; }
done
chmod +x "$SCR/statusline.sh" "$SCR/install.sh"
# 指令檔與腳本內寫死的 python3 換成這台實際有的直譯器
if [ "$PY" != "python3" ]; then
  for f in "$CMD/last-word.md" "$CMD/pickup.md"; do
    "$PY" - "$f" "$PY" <<'PYSUB'
import sys; p, py = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read().replace("python3 ", py + " ")
open(p, "w", encoding="utf-8").write(s)
PYSUB
  done
fi

# 試跑狀態列一次
out=$(printf '{"model":{"display_name":"Claude"},"workspace":{"current_dir":"%s"},"session_id":"install-test","context_window":{"used_percentage":12}}' "$HOME" | bash "$SCR/statusline.sh" 2>&1)
case "$out" in *"12%"*) ;; *) echo "❌ 狀態列腳本試跑失敗：$out"; exit 1 ;; esac
rm -f "$CLAUDE/.handoff-markers/install-test"

# 接上 statusLine（有既有設定就不碰）
"$PY" - "$SETTINGS" "$SCR/statusline.sh" "${1:-}" <<'PY'
import json, os, shutil, sys
p, script, flag = sys.argv[1], sys.argv[2], sys.argv[3]
s = {}
if os.path.exists(p):
    try:
        s = json.load(open(p))
    except Exception as e:
        print(f"⚠ settings.json 不是合法 JSON（{e}），狀態列未接上，請手動處理"); sys.exit(0)
    shutil.copy(p, p + ".bak-handoff")
cur = (s.get("statusLine") or {}).get("command", "")
want = f"bash {script}"
if cur and cur != want and flag != "--force-statusline":
    print(f"ℹ 已有狀態列設定未覆蓋：{cur}")
    print("  要換成 handoff 的：bash ~/.claude/scripts/handoff/install.sh --force-statusline")
    sys.exit(0)
s["statusLine"] = {"type": "command", "command": want}
json.dump(s, open(p, "w"), ensure_ascii=False, indent=2)
open(p, "a").write("\n")
print("✅ 狀態列已接上（備份在 settings.json.bak-handoff）")
PY

cat <<'EOF'
✅ handoff 安裝完成
  收工前打 /last-word　　開新對話打 /pickup
  終端機最底下那行超過 40% 會變紅並跳通知，那就是收工訊號
  （指令要在下一個新對話才會出現；已開著的對話打 /reload-skills）
EOF
