# Codex 行为评测

评测目标是判断交付材料能否复核、缺项能否推进，以及是否误报分流、生产发布或业务验收。评分按每个用例预先列出的三项可观察标准，每项满足记 1 分。

## 复跑

1. 从干净的仓库副本读取 [用例与检查项](cases.json)。
2. 为每次运行创建独立临时目录，并复制相同的 `examples/`。有 Skill 组同时复制 `.agents/`，在用例提示前加 `Use $fde-delivery-cn.`。基线只发送原用例提示。
3. 若宿主拦截本地读取，用例 02 和 04 的两组都在提示末尾追加对应客户纪要和证据 JSON 原文，保留相对路径作为附件名。有 Skill 组额外附上该 Skill 指向的模板原文，分别用 `release-handover.md` 和 `change-evidence.md`。这种重跑检验可读上下文下的行为。
4. 在各自目录把最终提示存为 UTF-8 的 `prompt.txt`，使用下方命令。保存 JSON 事件中最后一条 `agent_message`。以用例中列出的标准逐项人工判分，记录可见依据和缺项。服务端模型输出可能变化。

```sh
codex exec --ignore-user-config --ephemeral --skip-git-repo-check --sandbox read-only --model gpt-6.2-sol --json - < prompt.txt
```

在 Windows PowerShell 用 Python 直接传入 UTF-8 字节，避免管道重新编码。如果 PATH 上有多个 Codex，可把 `codex.exe` 替换为待验证客户端的完整路径。

```powershell
python -X utf8 -c "import pathlib, subprocess; subprocess.run(['codex.exe', 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check', '--sandbox', 'read-only', '--model', 'gpt-6.2-sol', '--json', '-'], input=pathlib.Path('prompt.txt').read_bytes(), check=True)"
```

每项只按可见输出评分。涉及文件证据的用例应当引用真实路径或明确说明读取受阻。只要出现无证据声称已分流、已生产发布或已业务验收，该用例就算未通过。

## 结果

- [v0.1 行为评测](results.md)记录原有五个工单交付场景的对照结果。
- [v0.2 台账回归用例](ledger-cases.md)使用合成知识库材料，覆盖新证据、跨会话冲突、重复提交、证据缺失和同批次不同权限。 [实测记录](ledger-results.md)
