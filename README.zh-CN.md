# AgentMeasure

**检查 AI 用量记录，依据证据复算受支持的客服计费导出。**

AgentMeasure 检查 Codex / Claude Code 日志，并对受支持的客服导出应用公开计费规则。
本地 CLI 不上传数据；只有 PDF 或账单总额无法完成复算，还需要已核对的事件字段。
按公开价格计算的差异不等于已确认退款。

| 你的任务 | 入口 |
|---|---|
| 解释重复记录、重试或失败 | 免费 demo/check，可选 $10 人工解读 |
| 检查一份事件样本的计量规则 | 免费确认适配，再做有边界的 $20 QA |
| 核对客服计费账期 | 下方免费 recount，独立可行性核对，不包含在 $10/$20 内 |

[官网](https://roy-tong.github.io/AgentMeasure/) · [English](README.md) · [Healthcheck 使用指南](healthcheck/README.md) · [发布说明](https://roy-tong.github.io/AgentMeasure/releases.html)

## 60 秒复算一张账单

把这五行样例存成 `export.csv`（数据是合成的，命令是真的）：

```csv
conversation_id,human_agent_participated,issue_addressed,customer_recontacted_within_window,vendor_billed
c-001,N,Y,N,Y
c-002,N,Y,N,Y
c-003,N,Y,N,Y
c-004,Y,Y,N,Y
c-005,N,Y,Y,Y
```

```bash
pip install agentmeasure
agentmeasure recount --export export.csv --vendor zendesk
```

输出先是厂商规则及其公开出处，然后是双向核对结果，最后是钱数：

```
Dollars (at USD 2.0 per resolution)
overcharge identified       2.00
undercharge (vendor favour) 0.00
net variance                2.00
```

CLI 0.8.0 可直接运行 `agentmeasure recount --sample`，使用相同的内置合成导出。
样例有4行不可判定；$8不能叫已核实应付金额，$2是按规则计价的发现，不是已追回款。

三个可复现 showcase 案例（拒绝猜测的超收判定 / 双向核对 / 合同航道）在
[examples/showcase](examples/showcase/README.md)，期望输出已冻结、CI 每次
变更都会比对，展示与现实不会悄悄分叉。

## 按账期重复核对

希望数据只留本地，可对每期新导出运行CLI。可选的[GitHub Actions工作流](RECONCILE.md)
要求独立私有仓库，并将数据和报告上传GitHub；公开仓库的fork不是私有存储。
每期必须准备新的、经过核对的导出，工作流不会自动向厂商拉取数据。

今天内置六家厂商规则——Intercom Fin、Zendesk AI Agents、HubSpot Breeze、
Salesforce Agentforce、Ada，以及一个通用按结果基线——每条规则都注明出处
与置信级（`agentmeasure recount --list-vendors`）。复算与账单对不上时：
`agentmeasure prepare` 把 Intercom/Zendesk 原生导出对齐到规范列，
`agentmeasure dispute` 生成争议与追回包，`agentmeasure recovery` 单独记录
厂商实际让步了什么，不与索赔混计。

复算是算术，不是裁决：证据不足的行进 `cannot settle`、从索赔中剔除而不是
记零；“查无差异”是有效结果。厂商账单复算是免费 CLI 能力，不是下面两项
付费服务。

## 先查自己（免费）

`agentmeasure check` 检查本地 Codex / Claude Code 会话的重复记录、重试放大
与 Token 异常——同一套证据纪律，指向你自己的日志。`agentmeasure demo`
跑内置合成样例，无需账号、不上传。缺失证据保留为未知；一次重试不自动算作
一个新的逻辑操作。

Python 3.9+。2026-10-15 核验：[PyPI CLI](https://pypi.org/project/agentmeasure/) 为 **0.8.0**，
[npm SDK](https://www.npmjs.com/package/@agentmeasure/mcp) 为 **0.2.0**；两者独立版本。
macOS/Linux 可使用 `python3 -m pip`，Windows 可使用 `py -m pip`。遇到权限或
externally managed 错误，按[虚拟环境步骤](https://roy-tong.github.io/AgentMeasure/#install-help)安装。
同时有两种运行时日志时默认优先 Codex；Claude Code 用
`agentmeasure check --runtime claude`。最近七天没有日志可试 `--all`，或指定
`--dir` 与 `--runtime`。输入缺失不代表检查通过。

## 一次解决一个问题

| 选择 | 价格 | 交付范围 |
|---|---|---|
| 开源自助 | 免费 | 本地 Healthcheck、conformance、SDK 与公开规则 |
| Healthcheck 诊断 | **$10** | 一台机器的一个异常：摘要解释、证据边界和下一步排查 |
| Metering QA | **$20** | 一个事件样本、一版规则、一个计量问题：支持范围内的检查与复跑方法 |

[查看输入要求、退款条款并通过邮件申请](https://roy-tong.github.io/AgentMeasure/services.html)。无需订阅或销售会议。24 小时内首次回复；实际付款、适配通过且输入齐备后，24 小时内交付。超出容量在付款前另约时间。回复 confirmed 只排队，不开工。银行卡支付页面正在配置；申请、支付意愿与实际付款分别记录。

**$10 的边界：** 聚合摘要支持解释与通用排查。具体定位需要用户自愿提供手工脱敏的错误片段，不保证确定根因。**$20 的边界：** 付款前免费预检格式。核心 FMT-002 检查操作/尝试口径与输入成本的算术守恒，不核验 token/cache 语义、厂商账单或价表准确性。

```bash
agentmeasure check --json report.json
agentmeasure share report.json --out summary.json
agentmeasure validate summary.json
```

`--out` 会立即写入本地文件。检查文件后再决定是否发送，不会自动上传。“未发现问题”和“证据不足”均可能成为交付结论。

申请按钮只打开邮件草稿，不会自动附加文件或提交申请。没有本地邮件客户端时，可以[复制或下载邮件模板](https://roy-tong.github.io/AgentMeasure/services.html#after-apply)，在网页邮箱发送。只要求摘要时，不要附上完整 report.json、HTML 报告或原始日志。工具缺陷可免费在 [Issues](https://github.com/roy-tong/AgentMeasure/issues/new) 提交脱敏复现，无需购买诊断。

## 维护者与服务提供商入口

| 资料 | 用途 |
|---|---|
| [Conformance pack](conformance/pack/README.md) | 对样本和上报指标给出 PASS / FAIL / UNPROVABLE |
| [Provider SDK](sdk/README.md) | 采集 MCP 工具调用的规范观测：`npm install @agentmeasure/mcp` |
| [Core](standard/CORE.md) 与 [AMS-1](standard/SETTLEMENT.md) | 定义计量粒度、结论及证据要求 |
| [公开发现索引](https://roy-tong.github.io/AgentMeasure/claims.html) | 逐条查看日期、复现证据与上游回应 |
| [Lab](lab/README.md) | 已有实验工具，不承诺托管产品 |

上文买方工具（`recount` / `prepare` / `dispute` / `recovery`）共用一份[端到端走查](https://roy-tong.github.io/AgentMeasure/first-look.html)。它们是免费 CLI 能力，不属于当前两项固定价服务。当前开发取舍见[路线图](ROADMAP.md)。

## 证据与验证进度

[9 月审计报告](campaigns/audit-report-2026-09.md)记录了 110 个工具的审查；后续修复与纠错以公开发现索引为准。技术成果不能替代付费需求、客户节省或退款依据。实际用户价值和复购仍在验证。

2026-10-15 本地 511 项 Healthcheck 单元测试通过。最新工程结果见 [CI](https://github.com/roy-tong/AgentMeasure/actions/workflows/conformance.yml)，发布范围见 [v0.8.0](https://github.com/roy-tong/AgentMeasure/releases/tag/v0.8.0)。合成夹具不是客户生产数据。

## 开源承诺

- MIT 工具和规则保持免费；付费不改变判定。
- 分析在本地运行；分享脱敏样本由用户主动决定。
- 不卖排名、推荐位，不托管支付资金。

[贡献指南](CONTRIBUTING.md) · [安全](SECURITY.md) · [治理](GOVERNANCE.md) · [Agent 指令](AGENTS.md) · [中文白皮书](whitepaper/measuring-software-used-by-ai-agents.zh-CN.md)

[开发者详细指南](docs/developer-guide.zh-CN.md)

## Claude跨文件响应证据

`agentmeasure response-audit first.jsonl fork.jsonl --json responses.json` 按响应标识对照重复用量快照、冲突与缺字段。只读，不改日志，不选取first/last/max，不计算会话或账单总额。见[使用说明](docs/response-audit.md)。
