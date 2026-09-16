---
description: 接續上一段 — 讀本專案的交接單，回到上次進度與下一步，不用手動重貼長 prompt
argument-hint: "[可選：主題名，如 login-page；省略則列出所有交接單供選]"
allowed-tools: "Read Glob Bash(python3 *) AskUserQuestion"
---

你正在執行 `/pickup`，從交接單接續上一段工作。這是 `/last-word` 的另一半：上一段收工時把狀態寫進交接單，這裡把它載回來。

要接的主題名（使用者提供，可能為空）：$ARGUMENTS

逐步執行：

## Step 1 — 算出本專案的交接單目錄

把當前 cwd 絕對路徑的 `/` 全換成 `-` 當 `<cwd-slug>`（例：`/Users/amy/shop-site` → `-Users-amy-shop-site`），目錄是：
`~/.claude/handoffs/<cwd-slug>/`

## Step 2 — 找到要載入的交接單

- **有給 `$ARGUMENTS`** → 先試精確檔名 `<目錄>/$ARGUMENTS.yaml`。
  - 精確命中 → 進 Step 3。
  - 沒中 → 把 `$ARGUMENTS` 當關鍵字，Glob `<目錄>/*.yaml`，取檔名含這個字（不分大小寫）的：
    - 剛好 1 個 → 載入，回報一句「已模糊命中 `<主題名>`」
    - 多個 → 只把含關鍵字的丟 AskUserQuestion 讓使用者挑
    - 0 個 → 說明沒有這個主題，列出目錄下所有主題讓使用者選；若使用者要接的是沒收過工的舊對話，提示改用原生 `/resume`
- **沒給** → 一律列出所有交接單讓使用者選，不自動靜默接：
  1. Glob `<目錄>/*.yaml`。0 個 → 告訴使用者「這個專案還沒有交接單，可能是新專案、或還沒用 `/last-word` 收過工」，停在這，不要亂猜別的專案。
  2. 讀推薦主題：`python3 ~/.claude/scripts/handoff/handoff-scope.py read`
  3. 用 AskUserQuestion 列出所有主題（即使只有 1 個也列）：推薦主題排第一並標「目前對話綁定（推薦）」，其餘照 yaml 的 `updated` 日期新到舊。

## Step 3 — 把交接單講白話

用三五行摘要：
- **topic**：這個主題在做什麼
- **done**：上一段做到哪
- **remaining**：還剩哪些（照順序）
- **next_action**：下一個動作
- **notes**：有的話提醒雷點或待確認

看一眼 `updated` 日期，距今很久就提醒狀態可能過時、先確認。

**摘要給完不算結束**，立刻接著跑 Step 4。

## Step 4 — 綁定，然後接續

把 `X` 換成實際載入的主題名：

```bash
python3 ~/.claude/scripts/handoff/handoff-scope.py bind X
```

這讓收工時 `/last-word` 不帶參數也會存回同一份交接單。接著順手清 `/resume` 同名殘影：

```bash
python3 ~/.claude/scripts/handoff/session-prune.py --apply
```

回報「✅ 已綁定 `X`，收工打 `/last-word` 免帶參數」＋殘影清了幾筆，然後直接從 `next_action` 接起第一個動作。動工前若涉及不可逆動作，先確認。
