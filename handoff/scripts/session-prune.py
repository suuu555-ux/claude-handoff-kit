#!/usr/bin/env python3
"""
session-prune.py — 把「同名的舊 session 對話檔」移到垃圾桶，讓 /resume 清單一個名字只剩一筆。

背景（2026-09-04）：每次 /clear 都會新開一支 .jsonl 並沿用顯示名，舊檔留在 /resume 清單裡
變成同名殘影；原生 picker 沒有刪除鍵（2.1.260 官方文件查證），只能移檔。

規則：
  - 只看本專案目錄 ~/.claude/projects/<cwd-slug>/*.jsonl（cwd 用 --cwd 指定，預設 os.getcwd()）。
  - 「同名」＝ .jsonl 內最後一筆 customTitle 與本窗的相同（本窗名字讀 --name，預設從
    ~/.claude/sessions/<pid>.json 依 CLAUDE_CODE_SESSION_ID 取 name）。
  - 絕不動：本窗自己（CLAUDE_CODE_SESSION_ID）、任何活窗（~/.claude/sessions/*.json 的 sessionId）。
  - 移到 ~/.Trash/claude-sessions-<YYYY-MM-DD>/（.jsonl ＋ 同名子夾一起），可救回。
  - 預設 dry-run 只列清單；加 --apply 才真的移。
  - 交接單 handoffs/*.yaml 與 .bindings 一律不碰。

用法：
  python3 session-prune.py            # 列出會移哪些
  python3 session-prune.py --apply    # 真的移
  python3 session-prune.py --name knowledge --cwd /path/to/project --apply
  python3 session-prune.py --self-test   # 用假資料驗證判定邏輯（正向＋反向對照組）
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import sys
import tempfile

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
TITLE_RE = re.compile(r'"customTitle":"((?:[^"\\]|\\.)*)"')


def slug(cwd: str) -> str:
    return cwd.replace("/", "-")


def live_session_ids(sessions_dir: str) -> set:
    ids = set()
    for p in glob.glob(os.path.join(sessions_dir, "*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                ids.add(json.load(f).get("sessionId", ""))
        except Exception:
            pass
    ids.discard("")
    return ids


def my_name(sessions_dir: str, sid: str) -> str:
    for p in glob.glob(os.path.join(sessions_dir, "*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("sessionId") == sid:
                return d.get("name") or ""
        except Exception:
            pass
    return ""


def last_title(jsonl_path: str) -> str:
    """回傳該對話檔最後一次設定的 customTitle（改名以最後一次為準）；無則空字串。"""
    title = ""
    try:
        with open(jsonl_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if '"customTitle"' in line:
                    m = TITLE_RE.findall(line)
                    if m:
                        title = m[-1]
    except Exception:
        pass
    return title


def plan(project_dir: str, name: str, sid: str, live: set):
    """回傳要移走的 session id 清單（排除自己與活窗）。"""
    out = []
    for p in sorted(glob.glob(os.path.join(project_dir, "*.jsonl"))):
        s = os.path.basename(p)[:-6]
        if s == sid or s in live:
            continue
        if last_title(p) == name:
            out.append(s)
    return out


def move(project_dir: str, sids, trash_dir: str):
    os.makedirs(trash_dir, exist_ok=True)
    moved = []
    for s in sids:
        for src in (os.path.join(project_dir, s + ".jsonl"), os.path.join(project_dir, s)):
            if os.path.exists(src):
                dst = os.path.join(trash_dir, os.path.basename(src))
                if os.path.exists(dst):
                    dst += "." + dt.datetime.now().strftime("%H%M%S")
                shutil.move(src, dst)
                moved.append(dst)
    return moved


def self_test() -> int:
    tmp = tempfile.mkdtemp(prefix="session-prune-test-")
    proj = os.path.join(tmp, "proj")
    sess = os.path.join(tmp, "sessions")
    os.makedirs(proj)
    os.makedirs(sess)

    def w(sid, title=None, renamed_to=None):
        with open(os.path.join(proj, sid + ".jsonl"), "w") as f:
            f.write('{"type":"user","message":{"content":"hi"}}\n')
            if title is not None:
                f.write('{"type":"custom-title","customTitle":"%s"}\n' % title)
            if renamed_to is not None:
                f.write('{"type":"custom-title","customTitle":"%s"}\n' % renamed_to)
        os.makedirs(os.path.join(proj, sid), exist_ok=True)

    w("me", "knowledge")                     # 自己 → 不動
    w("old1", "knowledge")                   # 同名舊檔 → 移
    w("old2", "knowledge")                   # 同名舊檔 → 移
    w("live1", "knowledge")                  # 同名但活窗 → 不動
    w("other", "woodbee")                    # 不同名 → 不動
    w("renamed", "knowledge", "woodbee")     # 曾叫 knowledge 後改名 → 不動（以最後一次為準）
    w("noname")                              # 無名 → 不動
    with open(os.path.join(sess, "1.json"), "w") as f:
        json.dump({"sessionId": "live1", "name": "knowledge"}, f)
    with open(os.path.join(sess, "2.json"), "w") as f:
        json.dump({"sessionId": "me", "name": "knowledge"}, f)

    live = live_session_ids(sess)
    got = plan(proj, "knowledge", "me", live)
    expect = ["old1", "old2"]
    ok = got == expect
    print("判定：", "PASS" if ok else "FAIL", "得到", got, "預期", expect)
    # 反向對照：名字改成不存在的，必須零命中
    got2 = plan(proj, "nothing-here", "me", live)
    ok2 = got2 == []
    print("反向對照（不存在的名字須零命中）：", "PASS" if ok2 else "FAIL", got2)
    # 實際移動一次，驗 .jsonl 與子夾都走了、其餘都在
    trash = os.path.join(tmp, "trash")
    move(proj, got, trash)
    left = sorted(os.listdir(proj))
    ok3 = all(x not in left for x in ("old1.jsonl", "old1", "old2.jsonl", "old2")) and \
        all(x in left for x in ("me.jsonl", "live1.jsonl", "other.jsonl", "renamed.jsonl", "noname.jsonl"))
    print("移檔：", "PASS" if ok3 else "FAIL", "剩下", left)
    shutil.rmtree(tmp)
    return 0 if (ok and ok2 and ok3) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cwd", default=os.getcwd(), help="session 起點 cwd（算 projects 子目錄用）")
    ap.add_argument("--name", default=None, help="要清的顯示名；預設讀本窗的名字")
    ap.add_argument("--apply", action="store_true", help="真的移；預設只列清單")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    sessions_dir = os.path.join(CLAUDE, "sessions")
    project_dir = os.path.join(CLAUDE, "projects", slug(os.path.abspath(a.cwd)))
    if not os.path.isdir(project_dir):
        print("找不到專案目錄：", project_dir)
        return 2
    name = a.name or my_name(sessions_dir, sid)
    if not name:
        print("本窗沒有顯示名（未 /rename），不知道要清哪個名字；用 --name 指定。")
        return 0
    live = live_session_ids(sessions_dir)
    targets = plan(project_dir, name, sid, live)
    if not targets:
        print(f"「{name}」沒有同名舊檔可清（專案目錄 {project_dir}）。")
        return 0
    print(f"「{name}」同名舊檔 {len(targets)} 筆（本窗 {sid[:8] or '?'} 與活窗已排除）：")
    for s in targets:
        p = os.path.join(project_dir, s + ".jsonl")
        mt = dt.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m-%d %H:%M")
        print(f"  {s}  {mt}  {os.path.getsize(p)//1024} KB")
    if not a.apply:
        print("（dry-run，加 --apply 才會移到垃圾桶）")
        return 0
    trash = os.path.join(HOME, ".Trash", "claude-sessions-" + dt.date.today().isoformat())
    moved = move(project_dir, targets, trash)
    print(f"已移 {len(moved)} 項到 {trash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
