# handoff — Claude Code 收工交接

Claude Code 的對話聊久了會變笨、`/clear` 之後又要從頭解釋。這個工具把「收工寫便條、開工讀便條」變成兩個指令。

## 怎麼用

| 時機 | 打什麼 | 結果 |
| --- | --- | --- |
| 收工前、`/clear` 前 | `/last-word` | Claude 把「做到哪、剩什麼、下一步」寫成便條 |
| 開新對話 | `/pickup` | Claude 讀便條，直接接著做 |

便條存在 `~/.claude/handoffs/`，不會進你的專案 repo。每個專案各自一張，不互蓋。

終端機最底下會多一行 `Claude · 專案名 · ▮▮▯▯▯ 41%`，是這個對話用掉的容量。過 40% 會跳系統通知，看到就打 `/last-word`。

## 安裝

把這段貼進 Claude Code：

```
請幫我安裝 handoff 收工交接工具：
1. 執行：curl -fsSL https://raw.githubusercontent.com/suuu555-ux/claude-handoff-kit/main/install.sh | bash
2. 把印出的結果給我看。若說「已有狀態列設定未覆蓋」，先問我要不要換。
3. 用三句話告訴我收工打什麼、開工打什麼、什麼通知代表該收工。
```

或自己在終端機跑：

```bash
curl -fsSL https://raw.githubusercontent.com/suuu555-ux/claude-handoff-kit/main/install.sh | bash
```

## 需要什麼

- **macOS**：不用裝東西。
- **Windows**：Git for Windows（Claude Code 本來就要）＋ Python 3（安裝時勾「Add python.exe to PATH」）。⚠ 還沒實機測過，有錯誤就把原文貼給 Claude。
- **Linux**：python3、curl。

## 移除

```bash
bash ~/.claude/scripts/handoff/install.sh --uninstall
```

便條會留著。

## 進階

- 通知門檻改 50%：加一行 `export HANDOFF_THRESHOLD=50`，macOS 放 `~/.zshenv`，Windows／Linux 放 `~/.bashrc`。
- 同專案多張便條：`/last-word login-page`、`/pickup login-page`。
- 更新：再跑一次安裝那行。
