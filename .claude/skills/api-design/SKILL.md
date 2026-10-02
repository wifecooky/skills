---
name: api-design
description: "Use when designing, reviewing, or evolving HTTP/public APIs — new endpoints, breaking-change decisions, versioning, authentication choices, idempotency, rate limiting, pagination, optional fields. Triggers: API 设计, 接口设计, 新增端点, breaking change, 版本化, versioning, idempotency, 幂等, rate limit, 限流, pagination, 分页, API review."
metadata:
  source: https://www.seangoedecke.com/good-api-design/ (Sean Goedecke, 2025-08-24)
---

# API Design: 接口是承诺，不是作品

## 核心原则

1. *好的 API 毫无惊喜*。用户花在思考 API 上的每一秒都是浪费。设计目标：不读文档就大致会用。REST 流行不是因为更好，而是因为足够熟悉。
2. *WE DO NOT BREAK USERSPACE*。公开 API 发布即冻结：只能加字段，永远不能删字段、改类型、动结构（如 `user.address` 挪到 `user.details.address`）。"更整洁"不是理由。
3. *版本化是必要之恶*。破坏性变更唯一的合法途径是新旧并存（`/v1/` 路径或 header），但每加一版所有端点翻倍维护，翻译层抽象必然泄漏。Last resort。
4. *API 形状追随产品的基本资源*。资源模型烂，API 必然烂——UI 能藏住的技术债在 API 里裸奔。先修资源模型，再谈接口。

## 速查表

| 场景 | 做法 |
|------|------|
| 认证 | 支持长效 API key（OAuth 可并存但不可唯一）。用户不全是工程师，跑通第一个脚本 > 理论安全性 |
| 写操作 | 支持幂等键（idempotency key），服务端见过即跳过。存 Redis、数小时过期即可；支付等高危场景需与数据库原子协调 |
| 读/删操作 | 天然幂等，不需要幂等键（DELETE 同一 ID 重试只删一次） |
| 限流 | API 以代码速度被调用。限流 + 按客户熔断开关 + 响应头给配额（`X-Limit-Remaining` / `Retry-After`） |
| 分页 | 可能变大的数据集一律游标分页（`WHERE id > cursor`），offset 越翻越慢且事后迁移代价极高；响应带 `next_page` |
| 贵的字段 | 默认关闭，用 `includes` 参数显式索取。GraphQL 是此思路的极端形态，多数场景过度设计 |
| 消费端 | 解析时忽略未知字段——上游加字段不是你崩溃的理由 |
| 内部 API | 规则放松（可破坏性变更、认证随意），但关键操作照样要幂等 |

## 常见错误

- 为"整洁"改字段名/结构 → 下游千百个软件崩坏。HTTP 的 referer 拼错几十年不改，就是这个理
- 幂等键做成必选 → 挡住非工程师用户。可选，文档写清楚
- 用 offset 分页上线，数据涨到几十万行才发现每页比上页慢 → 一开始就该用游标
- 单请求做大量工作的端点不设限流 → 总有人拿它搭你想不到的东西（真实案例：拿"通知全体用户"API 搭聊天室，打死后端）
- 指望优雅 API 拯救产品 → API 质量是边际特性，只在产品打平时起作用；但*完全没有* API 会丢单
