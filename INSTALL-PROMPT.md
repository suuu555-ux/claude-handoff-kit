# 安裝提示詞

把下面整段貼進 Claude Code 送出，Claude 會自己裝好並說明用法。

```
請幫我安裝 handoff 收工交接工具：
1. 執行：curl -fsSL https://raw.githubusercontent.com/suuu555-ux/claude-handoff-kit/main/install.sh | bash
2. 把印出的結果給我看。若說「已有狀態列設定未覆蓋」，先問我要不要換。
3. 用三句話告訴我收工打什麼、開工打什麼、什麼通知代表該收工。
```

Windows 的話，先確認 `python --version` 跑得出 3.x；跑不出就裝 Python 3（勾「Add python.exe to PATH」），重開終端機再貼上面那段。

## 之後怎麼用

- 收工前：`/last-word`
- 開新對話：`/pickup`
- 終端機最底下那行過 40% 跳通知：該收工了

## 移除

```bash
bash ~/.claude/scripts/handoff/install.sh --uninstall
```

便條會留著。
