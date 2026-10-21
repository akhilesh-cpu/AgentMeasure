# chenhz01-001（10/14 交付）— 本地 agent 运行时 74 行生产衍生观测

> 来源：@chenhz01 于 2026-10-14 17:56Z 在 issue #6 交付（Path A，自带 validator exit 0）；原帖=roy-tong/AgentMeasure#6 issuecomment 两个长评论。
> 署名归 @chenhz01；本仓只作投影与守卫（manifest sha256），非 endorsement。
> **Claim boundary（贡献者声明，逐字保留）**：production-derived——本人机器上的真实工作会话，连续 22 次 attempt 窗口；无 payload 内容/文件路径/命令文本/提示词或响应文本；非 conformance pass，非对 AgentMeasure 的一致性声明。

## 自带发现（贡献者原文要点）
1. **availability 不可证**：在该运行时，工具结果对后续模型调用的"可用性"无法从 provider 侧观测——result_consumed 只能证明"进入过上下文"，不能证明"被读过"。
2. **自报膨胀**：22 次 attempt 发生在 2 个计费请求内（per model request, token-metered）——按请求计费的平台上，attempt 级活动对账单不可见。

## 文件
- chenhz01-001.events.jsonl（74 行，spec agentmeasure-0.4，validate_jsonl.py exit 0）
- chenhz01-001.expected.json（expected verdicts：含 must_report_unprovable 条目）
- MAPPING.md（五问长答 + claim boundary + 未发三行说明 + 复现/出处）
- manifest.json（sha256 守卫：任一文件改动即失配）

## 与 conformance/vectors/external/chenhz01-001 的关系
vectors 侧为 10/8 availability certification fixture（runner 已接、SPEC-VERSION 钉 0.2.0-draft，drift check 在 conformance/runners/check_external_spec_versions.py）。本目录为 10/14 生产衍生超集交付（含 result_consumed 形状与 expected verdicts），按 #6 10/14 承诺入 conformance/external/ 原样保存；runner 接线待后续会话按 expected.json 增补。
