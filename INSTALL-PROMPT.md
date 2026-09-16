# 安裝提示詞

把下面整段複製，貼進 Claude Code 的對話框送出。Claude 會自己完成安裝並跟你說明用法。

```
請幫我安裝 handoff 這個 Claude Code plugin，照順序做，每步做完回報結果再做下一步：

1. 執行 /plugin marketplace add <你的GitHub帳號>/claude-handoff-kit
2. 執行 /plugin install handoff@su-kit
3. 執行 /handoff:setup，把 40% 容量提醒的狀態列接上我的設定（它會先備份 ~/.claude/settings.json 再改；如果我已經有別的狀態列，先問我再換）
4. 全部做完後，用三句白話告訴我：
   - 以後要收工、要 /clear 之前要打什麼
   - 開新對話要接上次的工作要打什麼
   - 看到什麼通知代表該收工了
```

## 之後怎麼用

- 收工前：`/handoff:last-word`
- 開新對話：`/handoff:pickup`
- 終端機最底下那行超過 40% 變紅、跳通知：就是收工訊號

## 移除

```
/plugin uninstall handoff@su-kit
```

狀態列設定要自己從 `~/.claude/settings.json` 拿掉 `statusLine` 那段（安裝時的備份在 `~/.claude/settings.json.bak-handoff`）。
