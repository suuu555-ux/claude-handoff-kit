---
description: 首次安裝後跑一次 — 把 40% 收工提醒的狀態列接上 Claude Code 設定
allowed-tools: "Read Edit Write Bash(python3 *) Bash(bash *) Bash(ls *) Bash(cp *)"
---

你正在執行 `/handoff:setup`。目的：讓「對話容量用到 40% 就跳通知」的狀態列真的生效。Plugin 本身不能改狀態列設定，所以由你來改使用者的 `~/.claude/settings.json`。

逐步執行：

1. **確認腳本存在**：`ls -la ${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh`，並確保可執行（不行就 `chmod +x`）。

2. **試跑一次**：
   ```bash
   printf '{"model":{"display_name":"Claude"},"workspace":{"current_dir":"%s"},"session_id":"setup-test","context_window":{"used_percentage":12}}' "$PWD" | bash ${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh; echo
   ```
   應該印出類似 `Claude · <專案名> · ▯▯▯▯▯ 12%` 的一行。沒印出就停下回報錯誤，不要往下。

3. **備份再改設定**：`cp ~/.claude/settings.json ~/.claude/settings.json.bak-handoff`（檔案不存在就跳過備份，稍後新建）。讀 `~/.claude/settings.json`：
   - 若已有 `statusLine` 且指向別的腳本 → 停下，用一句話問使用者要不要換成本 plugin 的（不要自作主張覆蓋）。
   - 否則寫入或合併這一段（其他既有設定原封不動）：
     ```json
     "statusLine": {
       "type": "command",
       "command": "bash <這裡填 ${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh 展開後的絕對路徑>"
     }
     ```
   寫完用 `python3 -c "import json;json.load(open('$HOME/.claude/settings.json'))"` 驗證仍是合法 JSON。

4. **回報**：告訴使用者「狀態列會在下次開新對話時出現在終端機最底下；用量過 40% 會跳一次通知，看到就打 `/handoff:last-word`」。macOS 若沒跳通知，請到「系統設定 → 通知」確認終端機或 Script Editor 的通知沒被關掉。
