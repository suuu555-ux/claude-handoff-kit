#!/usr/bin/env python3
"""handoff scope 共用管線（last-word / pickup 共用）。

子指令：
  read          讀當前 session 的 scope：綁定記號優先，退 session /rename 顯示名，皆無印空字串
  bind <scope>  寫綁定記號（session id → scope），附成功/失敗回報

sid 來源＝環境變數 CLAUDE_CODE_SESSION_ID；綁定記號存 ~/.claude/handoffs/.bindings/<sid>。
並行 session 各有獨立 sessionId → 互不干擾。顯示名退路不可靠（/clear 會清空），僅當備案。
"""
import glob
import json
import os
import pathlib
import sys

BINDINGS = pathlib.Path(os.path.expanduser("~/.claude/handoffs/.bindings"))
SESSIONS_GLOB = os.path.expanduser("~/.claude/sessions/*.json")


def sid():
    return os.environ.get("CLAUDE_CODE_SESSION_ID", "")


def cmd_read():
    s = sid()
    if not s:
        print("")
        return 0
    b = BINDINGS / s
    if b.is_file():
        print(b.read_text().strip())
        return 0
    # 退路：session /rename 顯示名
    for f in glob.glob(SESSIONS_GLOB):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get("sessionId") == s:
            print(d.get("name", ""))
            return 0
    print("")
    return 0


def cmd_bind(scope):
    s = sid()
    if not s:
        print(f"⚠ 無 session id，未寫入綁定——收工請帶參數 /last-word {scope}")
        return 1
    BINDINGS.mkdir(parents=True, exist_ok=True)
    (BINDINGS / s).write_text(scope)
    print(f"綁定完成 scope={scope}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "read":
        sys.exit(cmd_read())
    if len(sys.argv) >= 3 and sys.argv[1] == "bind":
        sys.exit(cmd_bind(sys.argv[2]))
    print(__doc__)
    sys.exit(2)
