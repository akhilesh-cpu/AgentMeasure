# rajudandigam-002 — AgentInspect 6.31.20 identity round-trip evidence（部分交接）

> 来源：Raju Dandigam（AgentInspect 维护者）2026-10-11 邮件交付（原信存档=市场推广/GTM工作区/回复-Raju-身份丢失与fixture包-20261011.md）。
> 署名归 @rajudandigam；本仓只作投影与守卫，非 endorsement。**Partial handoff（他明示）**：生成器退出码≠完全 conformance；maxAttempts=2 的重复投递 JSONL 在 duplicate-attempt-id 上失败而其 OTLP 导出通过；maxAttempts=1 双双失败（在生成器中掩盖该分歧）；identity collision 为独立对照，partial identity 未知。
> 口径：**无已测客户计费影响或财务成本**（他主动声明，本仓照录不改写）。

## 复现
- clone github.com/rajudandigam/agent-inspect @ 8c7f674eeb0c3db1b7851b05ae93a2277826a011，pnpm 9.15.0 --frozen-lockfile，pnpm build
- 生成器：`node scripts/f04-otlp-identity-evidence.mjs ./otlp-evidence`
- 附加边界：生成文件放消费者侧 ../otlp-evidence，跑 probe（.mjs.txt 改 .mjs）——修复前应 exit 1

## 文件
O01-O07 证据组（source JSONL / default OTLP / contract-results 三件）；覆盖：一操作两尝试（O01）、三尝试（O02）、两操作四尝试（O03）、重复投递（O05）、第二物理运行（O04）、等参数异操作（O07）、partial identity（O06）。
对应我方语义：operation/attempt/retry/physical-run 身份经 source→export 往返存活（6.31.20 修复项）；重复投递在 JSONL 与 OTLP 两面判定不一致=**我方家族一（重试/重发双计）的镜像边界**。
