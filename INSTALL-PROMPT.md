# 安裝提示詞

把下面整段複製，貼進 Claude Code 的對話框送出。Claude 會自己下載、安裝，然後跟你說明用法。

```
請幫我安裝 handoff 收工交接工具，照順序做：

1. 執行這行：curl -fsSL https://raw.githubusercontent.com/suuu555-ux/claude-handoff-kit/main/install.sh | bash
2. 把它印出的結果原樣給我看。若它說「已有狀態列設定未覆蓋」，先問我要不要換成 handoff 的再決定。
3. 如果我是 Windows，先確認 python --version 跑得出 3.x；跑不出就帶我去 python.org 裝（記得勾 Add to PATH），裝完重開終端機再回到第 1 步。
4. 用三句白話告訴我：
   - 以後要收工、要 /clear 之前要打什麼
   - 開新對話要接上次的工作要打什麼
   - 看到什麼通知代表該收工了
```

## 之後怎麼用

- 收工前：`/last-word`
- 開新對話：`/pickup`
- 終端機最底下那行超過 40% 變紅、跳通知：就是收工訊號

## 移除

```
bash ~/.claude/scripts/handoff/install.sh --uninstall
```

會拿掉兩支指令、腳本資料夾、以及它自己寫的狀態列設定；你的交接單 `~/.claude/handoffs/` 會留著。
