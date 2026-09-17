# handoff — Claude Code 的收工交接工具

給剛開始用 Claude Code 的人。解決兩個最常見的痛：

1. **對話越聊越長，突然變笨、忘記前面說過的事。** 因為每個對話有容量上限，滿了會自動壓縮。
2. **`/clear` 之後要重新解釋一遍「我做到哪、接下來要做什麼」。**

裝完多兩支指令和一條狀態列，把這兩件事變成固定動作。

## 它怎麼運作（白話版）

把它想成一張**便條紙**的循環：

- 快收工時打 `/last-word`：Claude 回顧這段對話，把「做到哪、剩什麼、下一步」寫進一張便條（一個 yaml 檔，存在 `~/.claude/handoffs/`，跟你的專案資料夾分開，不會弄髒 repo）。
- 之後 `/clear` 或關掉，都沒關係。
- 下次打 `/pickup`：Claude 讀那張便條，用三五行講給你聽，然後直接從「下一步」接著做。

另外一條**狀態列**顯示在終端機最底下：`Claude · 專案名 · ▮▮▯▯▯ 41%`。那個百分比是這個對話的容量用了多少。跨過 40% 時會跳一次系統通知叫你收工（macOS 通知中心、Windows toast、Linux notify-send），因為超過之後 Claude 的品質會開始掉，等它自動壓縮就來不及了。

## 安裝

把下面整段貼進 Claude Code 對話（完整版在 `INSTALL-PROMPT.md`）：

```
請幫我安裝 handoff 收工交接工具，照順序做：
1. 執行這行：curl -fsSL https://raw.githubusercontent.com/suuu555-ux/claude-handoff-kit/main/install.sh | bash
2. 把它印出的結果原樣給我看。若它說「已有狀態列設定未覆蓋」，先問我要不要換。
3. 用三句白話告訴我：收工要打什麼、開新對話要打什麼、看到什麼通知代表該收工。
```

或自己在終端機跑：

```bash
curl -fsSL https://raw.githubusercontent.com/suuu555-ux/claude-handoff-kit/main/install.sh | bash
```

## 兩支指令

| 指令 | 什麼時候打 | 它做什麼 |
| --- | --- | --- |
| `/last-word` | 要收工、要 `/clear` 之前，或看到 40% 通知 | 回顧對話、把殘餘工作寫進便條、檢查有沒有沒 commit 的改動、清 `/resume` 清單的同名殘影 |
| `/pickup` | 開新對話要接上次的工作 | 讀便條、講白話摘要、直接從下一步做起 |

多個專案各有各的便條，不會互蓋。同一個專案可以有多張（例如 `login-page`、`checkout`），打 `/pickup login-page` 指名要接哪張。

## 裝到哪、怎麼移除

```
~/.claude/commands/last-word.md、pickup.md      兩支指令
~/.claude/scripts/handoff/                        三支腳本＋這支安裝腳本
~/.claude/settings.json 的 statusLine             狀態列（原本有設定就不碰，會印提示）
```

移除：`bash ~/.claude/scripts/handoff/install.sh --uninstall`，便條會留著。

## 需要什麼

- **macOS**：python3 內建，什麼都不用裝。
- **Windows**：Claude Code 本來就要求裝 Git for Windows（指令在它的 Git Bash 裡跑）；另外要有 Python 3（python.org 下載，安裝時勾「Add python.exe to PATH」）。通知走 PowerShell 的系統 toast，不用裝模組。⚠ Windows 這條路還沒實機測過，安裝腳本印出的任何錯誤請原樣貼給 Claude。
- **Linux**：python3、curl；有 notify-send 才跳通知。

## 想改的地方

- 通知門檻：環境變數 `HANDOFF_THRESHOLD`（預設 40），例如加一行 `export HANDOFF_THRESHOLD=50`——macOS 放 `~/.zshenv`，Windows（Git Bash）與 Linux 放 `~/.bashrc`。
- 便條格式：見 `commands/last-word.md` 裡的 yaml 範本。
- 之後有新版：再跑一次安裝那行就會覆蓋更新。
