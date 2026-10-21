# VibeMirror-coder-001（10/21 交付）— HumanMirror x402 网关 56 行合成观测

> 来源：@chenhz01（=VibeMirror-coder 提供方）于 2026-10-21 17:50Z 在 issue #6 交付（Path C 辅助映射，五问映射已先期在 #6 约定）；提交仓库=github.com/chenhz01/VibeMirror-coder-001。
> 署名归 @chenhz01；本仓只作投影与守卫（manifest sha256），非 endorsement。
> **Claim boundary（贡献者声明，逐字保留）**：synthetic, provider-side, Base x402

## 自带发现（贡献者要点，原文见 expected.json 与 MAPPING.md）
1. **分组 UNPROVABLE 可测而非断言**：网关只观测 payer/tool/amount/时间，无买方 operation id——operation_id 0/13、retry_of 0/13、operation_resolution_coverage 0.0；"缺字段"本身由行承载，使 grouping UNPROVABLE 成为可测量结论。
2. **重试形状=二次结算**：exec-req-06 upstream_timeout 后再付款 exec-req-07 成功——按次计费单位下即双计形状，但该表面无法区分"重试"与"两次有意调用"，按分组 UNPROVABLE 报告、不作 overcharge 断言。
3. **advisory 选择率只能给下界**：4 个 advisory 决定中 2 个有观测选择（adv-0003/adv-0014），另 2 个窗口内沉默（有意 hold/离开/慢调用不可分）；2/4 不得发布为选择率。
4. **未付挑战零灌水**：15 挑战中 2 个止步于 presentation（pay-02/pay-13），attempts_from_unpaid_challenges=0。

## AgentMeasure 复测（2026-10-22，方法=docs/review-method/）
独立复算 30/30 项 must_assert 全一致（计数只从 canonical、价格只从 sidecar 结算行推导：safe_preflight 0.001 / action.release 0.002 USDC，合计 0.022 USDC on Base）。
一处 prose 更正（贡献者 negative-results policy 邀请）：交付帖把"两次成功"对写作 exec-req-12/14；数据实为 pay-08→pay-09（92s、同 payer、同工具）——pay-12/pay-14 为不同 payer、不同工具、相隔 45 分钟。expected.json 各值本身正确。

## 文件
- VibeMirror-coder-001.events.jsonl（56 行 canonical，spec agentmeasure-0.4，validate_jsonl.py exit 0 本仓复验）
- VibeMirror-coder-001.expected.json（49 项 must_assert + 6 UNPROVABLE + 1 UNOBSERVABLE + must_not_invent）
- VibeMirror-coder-001.provider-native.jsonl（32 行原始事件 sidecar：15 challenge/13 settlement/4 advisory；非 canonical，仅供映射复推）
- MAPPING.md（五问长答 + claim boundary + 形状清单，贡献者原文）
- manifest.json（sha256 守卫）

## runner 接线
待后续按 expected.json 增补（同 chenhz01-001 conformance/external 先例）；本目录先作原样保存与公开复测记录。
