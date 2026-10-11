# Contributing

AgentMeasure 是一个 measurement 标准项目。**问题定义和测量严谨性优先于功能数量。**

## 参与方式

| 想做什么 | 入口 |
| --- | --- |
| 讨论测量语义（什么算 usage / evidence / identity） | GitHub Discussions |
| 提出标准变更 | 先 Discussion 形成共识，再提 PR 修改 `spec/` |
| 修 adapter bug | Issue（adapter-bug 模板）→ PR |
| 报告测量偏差 | Issue（measurement-discrepancy 模板）——不同观测面数据不一致的实证 |
| 认领项目身份 | registry/project-identity PR（identity-claim 模板） |

## 原则（不接受违反）

1. **Evidence is derived, never self-declared**——adapter 不得自设证据等级
2. **Observation ≠ Invocation**——adapter 只产生 observation
3. **Raw stays local**——伪匿名必须在落盘前、内存内完成
4. **能力声明诚实**——官方 schema 没有的字段，宁可 unknown 不推断
5. **fail-closed**——时间解析失败、验签失败 → 拒绝，不假设

## 提交规范

- PR 必须通过 `conformance.py` 与 CI（.github/workflows/conformance.yml）
- 新增 adapter 必须附 capability matrix 更新（docs/adapters.md）
- 隐私相关改动必须附泄漏测试

## AI 协作贡献（AI-assisted contributions）

欢迎用 AI 辅助贡献，但规则如下（与项目证据纪律同源）：

1. **披露**：PR 描述里写明 `AI-assisted: yes/no`；用了吗、用在哪些部分。
2. **人对每行负责**：人类作者必须能解释并背书 PR 的每一行——"AI 写的我没细看"是拒收理由。
3. **不收批量 slop**：一次一个论证完整的报告，胜过十条泛泛的自动 issue/PR；模式化批量提交会被直接关闭。
4. **断言可复现**：每个测量/行为断言附 fixture、命令与期望输出；无法复现的断言按项目纪律标 UNPROVABLE，不合并不猜测。
5. 新增 conformance 向量请用脚手架：`agentmeasure conformance --new-vector <name>`，生成即过 CI 校验。

## 响应时效（维护者对自己的承诺）

- issue / PR **首次响应目标 ≤48 小时**（确认收到即可，不必立即解决）；实质性 review 一周内给出。
- 维护者目前是单人 + agent 协作，如果超时了，直接在帖子里 ping——催一下完全合理。
