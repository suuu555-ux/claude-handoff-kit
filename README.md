# handoff — Claude Code 的收工交接工具

給剛開始用 Claude Code 的人。解決兩個最常見的痛：

1. **對話越聊越長，突然變笨、忘記前面說過的事。** 因為每個對話有容量上限，滿了會自動壓縮。
2. **`/clear` 之後要重新解釋一遍「我做到哪、接下來要做什麼」。**

這個 plugin 給你三支指令和一條狀態列，把這兩件事變成固定動作。

## 它怎麼運作（白話版）

把它想成一張**便條紙**的循環：

- 快收工時打 `/handoff:last-word`：Claude 回顧這段對話，把「做到哪、剩什麼、下一步」寫進一張便條（一個 yaml 檔，存在 `~/.claude/handoffs/`，跟你的專案資料夾分開，不會弄髒 repo）。
- 之後 `/clear` 或關掉，都沒關係。
- 下次打 `/handoff:pickup`：Claude 讀那張便條，用三五行講給你聽，然後直接從「下一步」接著做。

另外一條**狀態列**顯示在終端機最底下：`Claude · 專案名 · ▮▮▯▯▯ 41%`。那個百分比是這個對話的容量用了多少。跨過 40% 時會跳一次 macOS 通知叫你收工，因為超過之後 Claude 的品質會開始掉，等它自動壓縮就來不及了。

## 安裝

把下面整段貼進 Claude Code 對話（也可以直接看 `INSTALL-PROMPT.md`）：

```
請幫我安裝 handoff 這個 Claude Code plugin，照順序做：
1. 執行 /plugin marketplace add <你的GitHub帳號>/claude-handoff-kit
2. 執行 /plugin install handoff@su-kit
3. 執行 /handoff:setup 把狀態列接上（它會備份我的 settings.json 再改）
4. 做完後，用三句話告訴我：以後收工要打什麼、開新對話要打什麼、看到什麼通知代表該收工。
```

## 三支指令

| 指令 | 什麼時候打 | 它做什麼 |
| --- | --- | --- |
| `/handoff:last-word` | 要收工、要 `/clear` 之前，或看到 40% 通知 | 回顧對話、把殘餘工作寫進便條、檢查有沒有沒 commit 的改動、清 `/resume` 清單的同名殘影 |
| `/handoff:pickup` | 開新對話要接上次的工作 | 讀便條、講白話摘要、直接從下一步做起 |
| `/handoff:setup` | 裝好後跑一次 | 把 40% 提醒的狀態列寫進你的 Claude Code 設定 |

多個專案各有各的便條，不會互蓋。同一個專案可以有多張便條（例如 `login-page`、`checkout`），打 `/handoff:pickup login-page` 指名要接哪張。

## 需要什麼

- macOS（通知用內建的 osascript；其他系統狀態列照跑、只是不跳通知）
- Claude Code 有 plugin 功能的版本
- python3（macOS 內建）

## 檔案結構

```
handoff/
  commands/last-word.md   收工儀式
  commands/pickup.md      接續
  commands/setup.md       接狀態列
  scripts/statusline.sh   狀態列＋40% 通知
  scripts/handoff-scope.py  記住「這個對話綁哪張便條」
  scripts/session-prune.py  清 /resume 同名殘影（移到垃圾桶，可救回）
  hooks/hooks.json        開新對話時若狀態列還沒接上，提醒一句
```

## 想改的地方

- 通知門檻：環境變數 `HANDOFF_THRESHOLD`（預設 40），例如在 `~/.zshenv` 加 `export HANDOFF_THRESHOLD=50`。
- 便條格式：見 `commands/last-word.md` 裡的 yaml 範本。
