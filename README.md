# FDE Delivery CN · 企业现场交付助手

一个面向国内企业前沿部署工程师（FDE）的 Codex Skill。它根据客户纪要、现场约束和运行证据，生成当前阶段可复核的勘察、试点、验收或交接记录。

例如，联调通过时，交付记录会写明验证的是哪个版本、在哪个环境、证据在哪里，并单独记录生产发布和客户签收状态。

## 用两个会话续接交付台账

这个案例使用合成的企业知识库试点材料。先把 [起始台账](examples/knowledge-base/ledger-before.md) 和同目录的 `evidence/` 复制到一个工作目录，保留相对位置。将台账副本作为两次会话共同的交付记录。

```powershell
$ledgerDemo = Join-Path '.demo-output' "kb-$(Get-Date -Format 'yyyyMMdd-HHmmss-fff')"
New-Item -ItemType Directory -Path $ledgerDemo
Copy-Item examples/knowledge-base/ledger-before.md (Join-Path $ledgerDemo 'ledger.md')
Copy-Item examples/knowledge-base/evidence $ledgerDemo -Recurse
```

1. **第一次会话**。使用 `$fde-delivery-cn`，提供台账副本、`KB-E01.md` 和 `KB-E02.md`，请 Codex 将检索联调和权限抽查的结果更新到台账副本。生产仍待排期，业务仍待签收。
2. **新会话**。提供更新后的同一份台账和 `KB-E03.md`，请 Codex 继续更新。两份报告对同一员工、查询和批次的权限结论相反。预期把权限事项标为待复核，保留两份证据，并明确由客户 IT 查日志和复测。
3. **再次提交同一证据**。请 Codex 重新处理 `KB-E03.md`。台账的事项和更新记录应保持原样。

见[回归用例](evals/ledger-cases.md)和[更新后的台账示例](examples/knowledge-base/ledger-after.md)。Skill 在工具可读写时更新指定台账；如果环境仅能读取材料，可让它输出拟修改内容。

## 运行工单演示

需要 Python 3.10+。演示用固定规则和合成工单模拟建议、人工确认与异常转人工，可离线运行。

```sh
git clone https://github.com/EthanZ-zh/fde-delivery-cn.git
cd fde-delivery-cn
python examples/ticket-triage/demo.py --out .demo-output/pending
python examples/ticket-triage/demo.py --decision approve --out .demo-output/approved
python examples/ticket-triage/demo.py --scenario offline --decision approve --out .demo-output/offline
```

| 演示 | 状态 | 结果 |
| --- | --- | --- |
| 默认等待确认 | `awaiting_confirmation` | 提议「IT 支持」，最终队列为空。 |
| 值班主管批准 | `routed` | 模拟分流到「IT 支持」，事件顺序为建议、批准、分流。[示例证据](examples/ticket-triage/evidence/approved/evidence.json) |
| 建议服务模拟离线 | `manual_review` | 即使传入批准参数，也会保留人工处理路径，最终队列为空。[示例证据](examples/ticket-triage/evidence/offline/evidence.json) |

每次调用按指定场景独立运行，在对应输出目录写入 `evidence.json`。同一输出目录会保留最近一次成功运行的记录。还可用 `--decision reject` 模拟人工拒绝，或用 `--scenario unknown` 模拟未知类别。

## 在 Codex 使用

在仓库根目录打开 Codex，选择 [fde-delivery-cn](.agents/skills/fde-delivery-cn/SKILL.md) 或在提示中显式提及 `$fde-delivery-cn`。仓库内的 Skill 目录供 Codex 发现。若在别的项目使用，把整个 `fde-delivery-cn` 目录复制到目标项目的 `.agents/skills/`，并将本仓库的 `LICENSE` 一并复制到该 Skill 目录以保留模板的版权和许可。 [Codex 技能指南](https://learn.chatgpt.com/docs/build-skills)

示例提示：

> 使用 $fde-delivery-cn，读取 `examples/ticket-triage/客户纪要.md` 和 `.demo-output/offline/evidence.json`，输出本次异常的交付证据记录。判断是否发生分流，说明谁接手以及恢复前需要验证什么。

Skill 可直接从当前阶段切入。首次沟通用现场勘察模板，准备 PoC 时用试点验收模板，异常复核或项目汇报用变更证据模板，上线与接手时用运维交接模板。客户已有表单时，可保留原表单并补齐证据和负责人。

## 验证

```sh
python -m unittest discover -s tests -v
```

五项测试覆盖等待、批准、拒绝、模拟离线和未知类别。[行为评测](evals/README.md) 记录 Codex 有无 Skill 的对照方法和结果。

演示验证的是模拟工单的行为和交付记录。实际客户的账号权限、发布和验收以客户环境及确认记录为准。工作流模板与演示代码的发布许可和复用来源可查阅 [MIT 许可证](LICENSE) 和 [上游致谢](NOTICE.md)。
