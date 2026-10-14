# AgentMeasure

**检查 Codex / Claude Code 日志中的重复记录、重试与 Token 异常，用可复现证据核对 Agent 计量。**

[官网](https://roy-tong.github.io/AgentMeasure/) · [English](README.md) · [Healthcheck 使用指南](healthcheck/README.md) · [发布说明](https://roy-tong.github.io/AgentMeasure/releases.html)

## 先在本地试用

```bash
pip install agentmeasure
agentmeasure demo                 # 合成样例，无需账号、不上传
agentmeasure check                # 检查本地 Codex / Claude Code 会话
```

样例展示覆盖范围、失败、重试链及可观测的 Token 信息。检查自己的日志时，缺失证据保留为未知；一次重试不自动算作一个新的逻辑操作。

Python 3.9+。2026-10-14 核验：[PyPI CLI](https://pypi.org/project/agentmeasure/) 为 **0.7.0**，[npm SDK](https://www.npmjs.com/package/@agentmeasure/mcp) 为 **0.2.0**；两者独立版本。

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

## 维护者与服务提供商入口

| 资料 | 用途 |
|---|---|
| [Conformance pack](conformance/pack/README.md) | 对样本和上报指标给出 PASS / FAIL / UNPROVABLE |
| [Provider SDK](sdk/README.md) | 采集 MCP 工具调用的规范观测：`npm install @agentmeasure/mcp` |
| [Core](standard/CORE.md) 与 [AMS-1](standard/SETTLEMENT.md) | 定义计量粒度、结论及证据要求 |
| [公开发现索引](https://roy-tong.github.io/AgentMeasure/claims.html) | 逐条查看日期、复现证据与上游回应 |
| [Lab](lab/README.md) | 已有实验工具，不承诺托管产品 |

[买方核账](https://roy-tong.github.io/AgentMeasure/first-look.html)保留为实验性工具参考，不属于当前两项固定价服务。当前开发取舍见[路线图](ROADMAP.md)。

## 证据与验证进度

[9 月审计报告](campaigns/audit-report-2026-09.md)记录了 110 个工具的审查；后续修复与纠错以公开发现索引为准。技术成果不能替代付费需求、客户节省或退款依据。实际用户价值和复购仍在验证。

2026-10-14 本地 477 项 Healthcheck 单元测试通过。最新工程结果见 [CI](https://github.com/roy-tong/AgentMeasure/actions/workflows/conformance.yml)，发布范围见 [v0.7.0](https://github.com/roy-tong/AgentMeasure/releases/tag/v0.7.0)。合成夹具不是客户生产数据。

## 开源承诺

- MIT 工具和规则保持免费；付费不改变判定。
- 分析在本地运行；分享脱敏样本由用户主动决定。
- 不卖排名、推荐位，不托管支付资金。

[贡献指南](CONTRIBUTING.md) · [安全](SECURITY.md) · [治理](GOVERNANCE.md) · [Agent 指令](AGENTS.md) · [中文白皮书](whitepaper/measuring-software-used-by-ai-agents.zh-CN.md)

[开发者详细指南](docs/developer-guide.zh-CN.md)
