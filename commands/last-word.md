---
description: 收工儀式 — 回顧這段對話、把殘餘工作寫進交接單、檢查未 commit，最後確認可以 /clear
argument-hint: "[可選：這段工作的主題名，如 login-page；省略則沿用 /pickup 綁定的名字]"
allowed-tools: "Bash(git *) Bash(python3 *) Read Write Edit Glob Grep AskUserQuestion"
---

你正在執行 `/last-word`，這是 `/clear` 之前的收工儀式。目標：把這段對話的價值存到對的地方，讓下一個對話能無痛接手，同時不讓 CLAUDE.md 無限膨脹。

這段工作的主題名（使用者提供，可能為空）：$ARGUMENTS

逐步執行下面六步。**刪檔、commit 這類不可逆動作前，一律先列清單請使用者確認**，不要先斬後奏。只動跟這段工作明確相關的東西。

---

## Step 0 — 蒐集現況（一次平行跑，不要逐條等）

沒有 git repo 的專案就跳過 git 那幾項，不要報錯：
- `git rev-parse --is-inside-work-tree`、`git branch --show-current`、`git status --short`、`git log --oneline -10`
- 找專案的 `./CLAUDE.md`（有就讀，通用規則要寫這裡）
- 讀本專案的交接單（若有）：先算出路徑（見 Step 2），能讀到就當「上一段做到哪」的底

用三五行摘要現況給使用者。

## Step 1 — 回顧這段對話

掃過整段對話，挑出三類東西（條列，要具體、可行動）：
- **卡點**：哪裡卡住、繞遠路、踩坑 → 下次怎麼避免
- **值得重複的做法**：哪個流程或指令這次特別順 → 值得變成慣例
- **CLAUDE.md 缺漏**：有沒有「早知道就好」的規則，現在的 CLAUDE.md 沒寫

然後把每一條歸位，各歸各位：

| 這條 learning 是什麼性質 | 寫到哪 |
| --- | --- |
| 通用規則，以後每次開工都該知道 | 專案的 `./CLAUDE.md`（append 一句祈使句到合適段落，別重寫整檔） |
| 暫時狀態，做到哪、剩什麼 | 交接單（Step 2） |
| 已經被 git commit 記到了 | 不用存，重複記沒意義 |

逐條回報你把它歸去哪、為什麼。

## Step 2 — 殘餘工作寫進交接單

殘餘工作與下一步**統一寫進交接單**，不要產一段散文叫使用者下次貼回來（那樣會掉細節）。原則是**累積更新同一份檔**，下個對話直接載入。

**算路徑：**
1. 專案鑰匙：把當前 cwd 絕對路徑的 `/` 全換成 `-`，當 `<cwd-slug>`（例：`/Users/amy/shop-site` → `-Users-amy-shop-site`）。不同專案因此不會互蓋。
2. 主題名（＝檔名）：依序解析，第一個命中就用——
   - 有 `$ARGUMENTS` → 字面照用，並同步綁定：`python3 ~/.claude/scripts/handoff/handoff-scope.py bind <主題名>`
   - 沒有 → 讀綁定：`python3 ~/.claude/scripts/handoff/handoff-scope.py read`，印出非空就用
   - 還是空 → 用 AskUserQuestion 問一個主題名（預設 `main`），選定後立刻 `bind`
3. 最終路徑：`~/.claude/handoffs/<cwd-slug>/<主題名>.yaml`（Write 會自動建父目錄）

**讀舊檔再更新**：路徑已有檔就先讀進來，在既有基礎上更新（`done` 把本段成果加在最上面、做完的 `remaining` 勾成 `[x]`、改寫 `next_action`），**不要整檔重寫洗掉歷程**。沒有就照下面格式新建。

```yaml
session: <主題名>
updated: <YYYY-MM-DD>
topic: <一句話：這個主題在做什麼>
done:                          # 本段成果放最上面，往下是歷史
  - "<這段做完的事>"
remaining:                     # 照順序，做完的勾 [x]
  - "[ ] <下一步>"
  - "[ ] <再下一步>"
next_action: <下個對話第一個該做的具體動作>
refs:
  branch: <branch 或 —>
  key_files: [<關鍵檔案路徑>]
notes: <可選：雷點、待確認事項>
```

⚠ 條目內文只要含半形「冒號＋空格」（例如 `server: nginx`），整條要用雙引號包住，否則 YAML 會解析失敗。寫完跑一次驗證：

```bash
python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" <交接單路徑> && echo YAML_OK
```

（沒裝 yaml 模組就用 `python3 -c "import json"` 跳過，並在回報說明未驗。）

寫完只回報一行續接指引：
> 下段續接：新對話跑 `/pickup <主題名>`。

## Step 3 — 檢查未 commit 的改動

有 git repo 才做。`git status --short` 若工作區是髒的：
- 列出有改動的檔，提醒「/clear 前先處理，免得遺失」
- 問清楚要不要 commit、commit 哪些，由使用者拍板；commit 指令一律點名檔案（`git commit -- <檔案>`），不用 `-A`
乾淨的話直接回報「無未提交變更」。

## Step 4 — 清掉 /resume 清單的同名殘影

每次 `/clear` 都會新開一支對話檔並沿用顯示名，舊檔留在 `/resume` 清單裡變成同名殘影。跑：

```bash
python3 ~/.claude/scripts/handoff/session-prune.py
```

有列出東西就加 `--apply` 真的移（移到 `~/.Trash/claude-sessions-<日期>/`，可救回）。自動排除本窗與所有活窗；0 筆就一句帶過。

## Step 5 — 收工檢查表

逐項打勾或標記待辦：
- ☐ learnings 已歸位（CLAUDE.md／交接單）
- ☐ 交接單已更新（含 remaining／next_action），續接指引已給
- ☐ 無未提交變更（或已明確決定先不 commit）
- ☐ /resume 同名殘影已清

全綠就明說「✅ 可以安心 /clear 了」。有沒處理完的就列出來，讓使用者決定補完還是知情後照樣 clear。
