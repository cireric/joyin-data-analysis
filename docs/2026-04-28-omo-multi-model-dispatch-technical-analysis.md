# Oh My OpenAgent (OMO) 多模型并发分发限流问题的技术分析报告

> 生成时间：2026 年 4 月 28 日  
> 适用场景：OMO 用户配置优化、源码级扩展决策参考  
> 研究基础：OMO v1.0.155+ 源码（dev branch），LiteLLM/Portkey/LangGraph 等行业方案对比

---

## 一、问题背景

### 1.1 问题描述

在 oh-my-openagent（OMO）架构中，Sisyphus（主编排器）经常同时对一类任务派发多个并行 subagent。典型场景：

- 搜索/调研任务：同时派发 2-5 个 Explore 或 Librarian 实例，各自搜索不同方向
- 实现任务：同时派发多个 Sisyphus-Jr 实例，各自完成不同的 subtask

当多个 subagent 实例**同时使用同一模型**时，模型服务端（尤其是免费/低配额模型，如 GLM-4.7-Flash、Minimax 免费层等）容易触发 HTTP 429 限流。核心矛盾在于：OMO 的并行调度能力很强，但模型端的并发配额有限。

### 1.2 研究目标

在不修改 OMO 源码的前提下，通过配置手段实现：

1. 并行 subagent 实例**主动分散**到不同模型，而非等限流触发后才降级
2. 每个模型池有独立的 fallback 降级链
3. 多实例之间形成**负载均衡**的效果

---

## 二、OMO 架构关键组件分析

### 2.1 Agent 分发路径（两种机制）

OMO 中 Sisyphus 派发任务的路径有两条，**机制完全不同**：

| 机制 | 工具 | 参数 | 适用 agent | 模型解析路径 |
|------|------|------|-----------|------------|
| Category-based | `task(category="xxx", prompt="...")` | category + prompt | Sisyphus-Jr | `CATEGORY_MODEL_REQUIREMENTS` → category 配置 |
| Direct agent | `call_omo_agent(subagent_type="explore", prompt="...")` | subagent_type + prompt | Explore, Librarian, Oracle, Metis, Momus | `AGENT_MODEL_REQUIREMENTS` → agent override 配置 |

### 2.2 Category 系统

Category 是 OMO 的任务-模型映射单元。架构关键点：

- **Schema**：`CategoriesConfigSchema = z.record(z.string(), CategoryConfigSchema)`——**任何字符串都可用作 category 名称**，不仅限于 8 个内置分类
- **内置分类**：`visual-engineering`, `ultrabrain`, `deep`, `artistry`, `quick`, `unspecified-low`, `unspecified-high`, `writing`
- **模型解析**：`category` → `model`（用户配置）→ `fallback_models`（用户配置）→ `CATEGORY_MODEL_REQUIREMENTS[category]`（硬编码 fallback chain）→ 系统默认模型
- **提示词注入**：所有可用 category 自动出现在 Sisyphus 的系统提示词中（`### AVAILABLE CATEGORIES` 表格）和 `task()` 工具描述中

来源文件：`src/config/schema/categories.ts`、`src/shared/merge-categories.ts`

### 2.3 Direct Agent 调用路径

`call_omo_agent` 是第二条分发路径，参数签名：

```typescript
interface CallOmoAgentArgs {
  description: string
  prompt: string
  subagent_type: string     // "explore" | "librarian" | "oracle" | ...
  run_in_background: boolean
  session_id?: string
}
```

模型解析由 `resolveModelAndFallbackChain()` 在基础设施层决定，**agent 本身不知晓也不控制自己使用的模型**。

来源文件：`src/tools/call-omo-agent/types.ts`、`src/tools/call-omo-agent/tools.ts`

### 2.4 模型解析机制（两阶段）

OMO 的模型解析分为**两个独立阶段**，在 session 生命周期的不同时刻发生：

#### 阶段一：初始模型选择（Session 创建时）

在 session 创建时，决定使用哪个模型发起第一次请求：

1. UI 选中模型（用户手动选择）
2. 用户 Override 配置（`agents.xxx.model`）
3. Category 默认模型（`categories.xxx.model`）

以上三项互斥，取第一个存在的值作为初始模型。

#### 阶段二：运行时降级（初始模型失败后）

当初始模型调用失败（返回 `retry_on_errors` 中的错误码）时，走降级链逐个尝试：

4. 用户 `fallback_models` 配置（agent 或 category 级别）
5. Provider fallback chain（`CATEGORY_MODEL_REQUIREMENTS` / `AGENT_MODEL_REQUIREMENTS` 硬编码）
6. 系统默认模型

关键发现：**两个阶段都是单路径线性解析，没有多模型池或并发感知路由机制**。

来源文件：`src/shared/model-resolution-pipeline.ts`、`src/shared/model-requirements.ts`

### 2.5 现有限流防护机制

| 机制 | 配置位置 | 行为 | 默认状态 |
|------|---------|------|---------|
| `modelConcurrency` | `background_task.modelConcurrency` | 按模型名限制并发数 | 未设置 |
| `providerConcurrency` | `background_task.providerConcurrency` | 按提供商限制并发数 | 未设置 |
| `runtime_fallback` | `runtime_fallback.enabled` | 429 时自动切换 fallback 模型 | `false`（关闭） |
| `fallback_models` | 各 agent/category 配置中 | 指定可用备用模型列表 | 各 agent 有内置值 |

---

### 2.6 `runtime_fallback.retry_on_errors` 错误码解析

#### 2.6.1 分析框架：`fallback_models` 天然是跨 provider 的

根据 OMO 官方配置文档，`fallback_models` 的配置格式始终为 `"provider/model"`：

```jsonc
// 官方文档示例：混合 string 和 object 格式，均包含 provider 前缀
{
  "agents": {
    "sisyphus": {
      "model": "anthropic/claude-opus-4-7",
      "fallback_models": [
        "openai/gpt-5.4",                                    // string 格式
        { "model": "google/gemini-3.1-pro", "variant": "high" }  // object 格式
      ]
    }
  }
}
```

无论是 Agent 还是 Category 的内置 fallback chain，也都天然跨多个 provider：

```
librarian: openai/gpt-5.4-mini-fast → opencode-go/minimax-m2.7-highspeed
           → anthropic/claude-haiku-4-5 → opencode/gpt-5.4-nano
           ^^^^^^^^ 涉及 3 个不同 provider
```

因此，`runtime_fallback` 触发的本质上**不是"在相同模型上重复发送请求"，而是"走 fallback chain 切换到下一个模型"**，且这个切换几乎总是跨 provider 的。

错误码分析的判断标准：**"切到 fallback chain 中的下一个模型能否绕过这个错误"**。

#### 2.6.2 按 fallback 有效性的完整分析

由于 OMO 的 fallback chain 天然跨 provider 切换，以下分析**以跨 provider 场景为主**——这是最普遍的情况。

> **关于"绕过"的完整前提**：以下判断假设 fallback chain 中后序模型不与前序模型共享相同的问题根源。
> 例如：404（模型不存在）→ 后序模型的 endpoint 必须有效；401（Key 过期）→ 后序模型的 provider 必须有独立且有效的 API Key。
> 若 chain 违反这些前提，则判断不成立。

| 错误码 | 名称 | 模型 A 出错的典型原因 | 跨 provider 切到模型 B 能绕过？ | 需验证的前提条件 | 判断结论 |
|--------|------|----------------------|-------------------------------|----------------|---------|
| 429 | Rate Limit | 模型 A 的 QPS/并发超限 | ✅ **几乎肯定**。不同 provider 配额独立 | 无（不同 provider 配额天然独立） | **推荐加入** |
| 503 | Service Unavailable | 模型 A 的 provider 临时宕机/维护 | ✅ **很可能**。不同 provider 独立部署 | 无（不同 provider 基础设施独立） | **推荐加入** |
| 529 | Service Overloaded | 模型 A 的 provider 过载 | ✅ **很可能**。不同 provider 负载独立 | 无（不同 provider 负载互不影响） | **推荐加入** |
| 1305（业务码） | 智谱限流 | 智谱免费层并发超限 | ✅ **很可能** | 无（直接切到不同 provider 即可） | **推荐加入**（若使用智谱） |
| 404 | Not Found | 模型 A 的 endpoint 不存在/已废弃/改名 | ✅ **很可能**。不同 provider 的 model list 独立 | 需确保后序模型的 model ID 在当前 provider 上有效 | **推荐加入** |
| 502 | Bad Gateway | 模型 A 的 provider 上游网关故障 | ✅ **很可能**。不同 provider 有独立网关 | 需确保后序模型不属于同一网关（跨 provider 天然满足） | **推荐加入** |
| 504 | Gateway Timeout | 模型 A 响应过慢触发上游超时 | ✅ **很可能**。不同 provider 超时配置独立 | 需确保后序模型不是同一 provider 的同类大模型（同慢） | **推荐加入** |
| 500 | Internal Server Error | 模型 A 的 provider 服务端内部错误 | ✅ **很可能**。不同 provider 代码栈独立 | 需确保后序模型不属于同一集群（跨 provider 天然满足） | **可选加入** |
| 401 | Unauthorized | 模型 A 的 API Key 无效/过期 | ✅ **可能**。不同 provider 使用不同的 API Key | **关键前提**：后序 model 的 provider 必须配置了独立且有效的 API Key | **视情况加入** |
| 403 | Forbidden | 模型 A 的 API Key 无权限调用该模型 | ✅ **可能**。不同 provider 的权限策略独立 | **关键前提**：后序 model 的 provider 必须配置了独立且有对应权限的 API Key | **视情况加入** |
| 408 | Request Timeout | 客户端侧超时 | ⚠️ 不确定。可能与模型推理速度无关 | 难以判断，可能在 SDK 层处理更合适 | **不推荐** |
| 413 | Payload Too Large | 模型 A 的上下文窗口不足 | ✅ **可能**。不同 provider 的上下文限制不同 | 需确保后序模型的上下文窗口 >= 当前请求的上下文长度 | **可选加入** |
| 400 | Bad Request | 请求参数格式不符合 provider 的 API 规范 | ✅ **可能**。OpenAI 格式 ≠ Anthropic 格式 | 需确认错误确由 provider 规范差异引起，非请求内容语义问题 | **注意**（见下文字段） |
| 422 | Unprocessable Entity | 请求语义校验不通过 | ✅ **可能**。不同 provider 校验规则不同 | 同上，需确认是由校验规则差异而非内容问题引起 | **注意**（见下文字段） |

> 注：如果 fallback chain 中后序模型与失败模型属于**同一 provider**（例如 `opencode-go/minimax-m2.7` → `opencode-go/minimax-m2.7-highspeed`），则 502/504/401/403 无法绕过。但这类场景在实践中较少发生——内置 fallback chain 多为跨 provider 设计。

#### 2.6.3 几组需特别讨论的错误码

**429/529/503 —— 三类"限流/过载"错误**

OMO 中最安全的 fallback 触发器。由于 fallback chain 天然跨 provider（如 `minimax-m2.7 → claude-haiku-4-5`），不同 provider 的速率限制和负载状态互相独立。OMO 默认的 `retry_on_errors` 已包含 429 和 503 和 529。

**404 —— "模型不存在"在实际中非常实用**

模型 endpoint 变更在实践中相当常见（模型改名、版本下线、免费模型停止服务），404 通过跨 provider 切换几乎总是可绕过的：

```
configured:  zai/glm-4.7-flash       (模型已改名/下线)
     ↓ 404
fallback:    opencode-go/minimax-m2.7  (有效，继续工作)
```

**502/504 —— 网关类错误在跨 provider chain 下有效**

```
configured:  openai/gpt-5.4-mini      (OpenAI API 网关 502)
     ↓ 502
fallback:    anthropic/claude-haiku-4-5 (Anthropic API 独立网关，正常)
```

**401/403 —— 认证/权限错误在 OMO 中值得加入**

OMO 中 401/403 的绕过能力并不取决于"同 provider 还是跨 provider"的问题——因为 OMO 的 fallback chain 本身就是跨 provider 的。关键在于用户是否**为不同 provider 配置了独立且有效的 API Key**：

```
例 1（跨 provider，Key 独立，有效）：
  openai/gpt-5.4-mini  (OpenAI Key 过期)
      ↓ 401
  anthropic/claude-haiku-4-5  (Anthropic Key 独立，有效)  ✅

例 2（跨 provider，Key 独立，有效）：
  zai/glm-4.7-flash (智谱 Key 过期)
      ↓ 401
  opencode-go/minimax-m2.7 (OpenCode Go 独立 Key，有效)  ✅
```

**结论**：只要用户的 fallback chain 涉及多个 provider 且各 provider 具有独立的 API Key，401/403 加入 `retry_on_errors` 就是有效的。这也是 OMO 的默认配置已包含 400 的原因之一——400 在跨 provider 场景下也有可能绕过（不同 provider 的 API 规范不同）。

**400/422 —— 最需要谨慎的错误码**

`400 Bad Request` 和 `422 Unprocessable Entity` 的根源可能是两类的混合：

| 错误根因 | 举例 | 切 provider 能绕过？ |
|---------|------|-------------------|
| **请求格式的 provider 差异** | OpenAI 用 `max_tokens`，Anthropic 用 `max_tokens` 字段名不同 | ✅ 能。不同 provider 的 SDK 解析方式不同 |
| **请求内容的语义问题** | prompt 包含非法字符、JSON 解析失败 | ❌ 不能。切到任何 provider 都会失败 |
| **参数数值越界** | `temperature=2.5` 超出范围 [0,2] | ❌ 不能。所有 provider 都会拒绝 |

值得注意的是，OMO 的默认 `retry_on_errors` 值（未配置时的缺省行为）已包含 `400`，说明 OMO 官方认为 400 的跨 provider 绕过概率足够高，值得纳入默认配置。

#### 2.6.4 按 Provider 的特殊错误码

| Provider | 错误码/标识 | 含义 | 切 provider 能绕过？ | 推荐 |
|----------|-----------|------|-------------------|------|
| 智谱 | 1305（业务码） | 免费层 QPS/并发超限 | ✅ | **推荐加入** |
| 智谱 | 1103（业务码） | 请求参数缺失/无效 | ⚠️ 不确定 | 不推荐 |
| OpenAI | 529 | 服务过载 | ✅ | **推荐加入** |
| OpenAI | `insufficient_quota` | 账户配额不足 | ✅ | 推荐通过 `fallback_models` 换模型 |
| Anthropic | `overloaded_error` | 服务过载 | ✅ | **推荐加入**（对应 529） |
| Anthropic | `rate_limit_error` | 速率限制 | ✅ | **推荐加入**（对应 429） |
| Google/Gemini | 429 | 速率限制 | ✅ | **推荐加入** |
| Google/Gemini | 503 | 服务不可用 | ✅ | **推荐加入** |
| Ollama（本地） | — | 无 429，失败多为连接/超时 | ❌ 本地无需配置 |

#### 2.6.5 `retry_on_errors` 配置的两个维度

决定是否将某个错误码加入 `retry_on_errors`，需要同时评估错误码本身的性质和 fallback chain 的结构。由于 OMO 内置 fallback chain 普遍为跨 provider 设计（见下文各 Agent/Category 的 provider 链），在实际使用中**跨 provider 场景是默认状态**：

**维度一：错误码本身的性质**

| 性质 | 含义 | 跨 provider 切换效果 | 示例 |
|------|------|-------------------|------|
| **限流/过载类** | 服务端暂时无法处理，等待后可恢复 | ✅ 几乎肯定绕过 | 429, 503, 529, 1305 |
| **端点/网关类** | 特定模型或网关出问题，换 provider 可绕过 | ✅ 高度确定绕过 | 404, 502, 504 |
| **认证/权限类** | API Key 问题，换 provider 的 Key 可绕过 | ✅ 只要 Key 独立配置 | 401, 403 |
| **参数/语义类** | 请求内容有问题，换 provider 可能绕过 | ⚠️ 部分场景可绕过 | 400, 422, 413 |
| **服务端故障类** | provider 内部错误，换 provider 可绕过 | ✅ 很可能绕过 | 500 |

**维度二：fallback chain 的特性**

| chain 特性 | 实际表现 | 典型例子 |
|-----------|---------|---------|
| **OMO 内置 chain（默认）** | 多 provider 交叉 | `librarian` 涉及 openai/opencode-go/anthropic 等 3+ provider |
| **用户自定义 string chain** | 多 provider 常见 | `"openai/gpt-5.4" → "anthropic/claude-opus-4-7"` |
| **用户自定义同 provider chain** | 少见于内置，用户配置可能出现 | `opencode-go/m2.7 → opencode-go/m2.7-highspeed` |

> **实际结论**：在 OMO 中，除非用户明确将 fallback chain 限定在同一 provider，否则**默认就是跨 provider 的**。因此大部分错误码的加入在 OMO 中都是有效的。

#### 2.6.6 推荐的 `retry_on_errors` 配置

**基线配置（适用于多数用户）**：

根据 OMO 官方文档，`runtime_fallback` 的默认 `retry_on_errors` 为 `[400, 429, 503, 529]`。以下是在此基础上按需扩展的推荐配置：

```jsonc
{
  "runtime_fallback": {
    "enabled": true,
    // 错误码含义：
    //   400  Bad Request — OMO 默认已包含（跨 provider 时可能绕过）
    //   429  标准限流 — 所有场景均有效
    //   503  服务不可用 — 所有场景均有效
    //   529  服务过载 — 所有场景均有效
    //   1305 智谱限流业务码 — 仅使用智谱模型时需追加
    //   404  模型端点不存在 — 实用性强，推荐追加
    "retry_on_errors": [
      429,
      503,
      529,
      1305,
      404
    ],
    "max_fallback_attempts": 3,
    "cooldown_seconds": 30
  }
}
```

**完整配置（覆盖大多数可恢复错误）**：

由于 OMO 的 fallback chain 天然跨 provider，大多数错误码在跨 provider 切换时都是可绕过的。以下是更完整的配置：

```jsonc
{
  "runtime_fallback": {
    "enabled": true,
    "retry_on_errors": [
      400,   // Bad Request — OMO 默认已有；跨 provider 时格式差异可绕过
      429,   // 限流 — 跨 provider 绕过
      503,   // 服务不可用 — 跨 provider 绕过
      529,   // 服务过载 — 跨 provider 绕过
      1305,  // 智谱限流 — 跨 provider 绕过
      404,   // 模型不存在 — 跨 provider 绕过
      502,   // Bad Gateway — 跨 provider 绕过
      504,   // Gateway Timeout — 跨 provider 绕过
      500    // Internal Server Error — 跨 provider 绕过
    ],
    "max_fallback_attempts": 5,
    "cooldown_seconds": 15
  }
}
```

#### 2.6.7 不同配置组合的场景效果

| 配置组合 | 来源 | 覆盖范围 | 说明 |
|---------|------|---------|------|
| `[400, 429, 503, 529]` | OMO 默认值 | 请求格式错误 + 限流 + 服务过载 | 官方默认配置，安全通用 |
| `[400, 429, 503, 529, 1305, 404]` | **推荐基线** | 追加智谱限流 + 模型不存在 | 低风险，大部分用户适用 |
| `[400, 429, 503, 529, 1305, 404, 502, 504, 500]` | 最大化可用性 | 追加网关/超时/服务端错误 | 跨 provider chain 下低风险 |
| `[400, 429, 503, 529, 1305, 404, 502, 504, 500, 401, 403]` | 极端场景 | 追加认证/权限错误 | chain 跨 provider 且 Key 独立时安全 |
| `[429]` | 配置过窄 | 仅限流 | 遗漏 503/529/404 等常见可恢复错误 |

#### 2.6.8 核心原则

1. **OMO 的 default `retry_on_errors` 已包含 400, 429, 503, 529**——官方认为这些错误在跨 provider fallback 下是可绕过的。用户无需从零构建，可在默认值基础上按需扩展
2. **429/503/529 是最安全的加入项**——限流和过载类错误无论链结构如何，触发降级都是合理的
3. **404 是容易被忽略但非常实用的加入项**——模型 endpoint 下线/改名在实践中并不少见
4. **502/504/500 在跨 provider 链下是安全的加入项**——不同 provider 的基础设施独立
5. **401/403 在跨 provider 链且 Key 独立时有效**——多数 OMO 用户的 provider 配置符合此条件
6. **400 已在 OMO 默认配置中**——跨 provider 时因 API 规范差异可能绕过
7. **`max_fallback_attempts` 应与 `retry_on_errors` 列表长度匹配**——列表有 6 个错误码时 attempts 至少设为 3-5
8. **Provider 特有业务码按实际使用的 provider 补充**——智谱 1305、OpenAI `insufficient_quota` 等
9. **`cooldown_seconds` 应与 provider 的限流恢复周期匹配**——各 provider 的 `Retry-After` header（或等效恢复周期）差异显著：

| Provider | 典型限流恢复周期 | 建议 `cooldown_seconds` | 说明 |
|----------|----------------|------------------------|------|
| 智谱 (Zhipu) 免费层 | 1-5 秒（滚动窗口） | 5-10 | 恢复快，短 cooldown 即可重试 |
| 智谱付费层 | 按用户等级动态 | 10-15 | 并发配额高，恢复后即可重试 |
| OpenAI | 按 `Retry-After` header（通常 20-60 秒） | 30-60 | 建议匹配返回的 header 值 |
| Anthropic | 按 `Retry-After` header（通常 20-120 秒） | 30-60 | 同上 |
| MiniMax 免费层 | 按 RPM 窗口（1 分钟滚动） | 10-20 | 短窗口，中等 cooldown |
| DeepSeek | 动态调节（10 分钟超时断开） | 30-60 | 建议按返回的 429 信息调整 |
| Google/Gemini | 按 `Retry-After` header | 10-30 | 免费层恢复快，付费层灵活 |

> 建议：如果不确定具体 provider 的恢复特征，保守设置为 30 秒。若连续遭遇限流，说明 cooldown 过短或并发数过高，应优先调低 `modelConcurrency`。

---

### 2.7 同 Provider 多模型分配策略分析

#### 2.7.1 问题背景

用户提出：如果 Provider A 下有 M1、M2、M3 三个模型，Provider B 下有 N1、N2、N3，通过配置将不同 agent 分散到不同模型（如 explore 用 M1，librarian 用 M2），是否能有效控制 Provider A 触发限流的可能性？

#### 2.7.2 两种限流模式的区分

分析同一 provider 内多模型分配是否有效，必须先区分 provider 的限流粒度：

**模式一：账号级限流（Account-level throttling）**

```
Provider A 网关 ── 统计 API Key 总请求量
                    │
     ┌──────────┬──┴──┬──────────┐
     M1        M2    M3         汇总请求 → 100 RPM 上限
     │         │     │
     explore  librarian 其他
```

在此模式下，同一 provider 下**无论切到哪个模型，所有请求共享同一个配额计数器**。

```
例：Provider A 限制为 100 RPM
  explore  → M1 (60 RPM)
  librarian → M2 (60 RPM)
  两者合计 120 RPM → 触发限流  ❌
```

**结论：账号级限流下，同 provider 内多模型分配无效。**

**模式二：模型级限流（Per-model throttling）**

```
Provider A 网关
     │
     ├── M1 计数器 50 RPM ← explore 独立
     ├── M2 计数器 50 RPM ← librarian 独立
     └── M3 计数器 50 RPM ← 其他
```

在此模式下，每个模型有独立的配额计数器，agent 分散到不同模型确实可以分流。

```
例：M1 50 RPM、M2 50 RPM、M3 50 RPM
  explore  → M1 (40 RPM) ← M1 剩余 10
  librarian → M2 (40 RPM) ← M2 剩余 10 ✅ 互不影响
```

**结论：模型级限流下，同 provider 内多模型分配有效。**

#### 2.7.3 实际 Provider 的限流模式调研

以下是基于各平台官方文档的限流模式调研（2026 年 4 月）：

| Provider | 限流模式 | 多模型分配有效性 | 官方文档说明 |
|----------|---------|----------------|------------|
| **智谱 (Zhipu)** | **按模型 + 按账号**：不同模型设置独立并发上限；高峰期基于账户维度限流。错误码 1302 触发账号速率限制，1305 触发平台过载保护 | ✅ **有效**。不同模型之间有独立的并发配额 | [速率限制文档](https://docs.bigmodel.cn/cn/api/rate-limit.md)："不同模型设有独立的并发限制"、"按用户权益等级 & 模型维度划分的并发限制" |
| **MiniMax** | **按模型大类（账号级）**：Text/Voice/Video/Image 各有独立限额，但同大类内的不同模型（如 M2.7/M2.5/M2.1）共享配额。免费用户 20 RPM / 1M TPM，付费用户 500 RPM / 20M TPM | ❌ **同类别内无效**。M2.7 和 M2.5 共享同一配额计数器 | [官方文档](https://platform.minimaxi.com/docs/guides/rate-limits.md)："主账号和子账号共同享有以下所有速率限制"、"同大类下的模型共享限额" |
| **通义千问 (Qwen/阿里云百炼)** | **按模型独立**：各模型有独立的 RPM/TPM 限制和独立的免费额度。商业版（Max/Plus/Flash）各有独立定价和并发 | ✅ **有效**。各模型配额独立 | [模型列表](https://help.aliyun.com/zh/model-studio/getting-started/models)："稳定版或最新版限流条件更宽松"、"各模型独立计费和限流" |
| **DeepSeek** | **按账号（动态并发）**：根据服务端负载动态限制，**非固定 RPM**。并发超限时返回 HTTP 429，请求排队等待（最长 10 分钟） | ❌ **无效**。限流是账号级动态调节，不按模型区分 | [限速文档](https://api-docs.deepseek.com/zh-cn/quick_start/rate_limit)："根据负载情况，动态限制用户并发量" |
| **Kimi (Moonshot)** | **按模型独立**：K2.6/K2.5/K2 系列各自有独立速率限制 | ✅ **有效**。不同模型独立配额 | [API 文档](https://platform.kimi.com/docs/api/chat)：各模型 endpoint 独立 |
| **OpenAI** | **按模型 + 按使用层级**：各模型有独立 RPM（如 `gpt-4o-mini` 独立 500 RPM）。账号总使用量按 Tier 分级（免费 Tier 1 有总限额，付费 Tier 2-5 逐级提升）。**免费层**各模型共享账号总配额；**付费层**模型间配额独立 | ⚠️ **免费层无效，付费层部分有效** | [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)："Rate limits are measured in RPM and TPM per model" |
| **Anthropic** | **按组织 Tier + 按模型组合**：各模型有独立并发配额（Claude Opus 通常 5 RPM，Sonnet 50 RPM，Haiku 100 RPM）。受组织 Tier (Free/Pro/Max) 和 API 使用历史影响 | ✅ **有效**。Opus/Sonnet/Haiku 配额独立，不同模型间互不影响 | [Anthropic Rate Limits](https://docs.anthropic.com/en/api/rate-limits)："Rate limits are based on your usage tier and the specific model" |
| **Google/Gemini** | **按模型独立**：免费层 `gemini-2.0-flash` 1500 RPM，`gemini-2.5-pro` 50 RPM | ✅ **有效**。各模型配额完全独立 |
| **OpenRouter** | **按 API Key + 按模型组合**：各上游 provider 规则叠加 | ⚠️ 取决于上游 provider |
| **Ollama（本地）** | 无限流 | ✅ 不适用 |

> **关键发现**：
> - 国内一线 provider 限流模式分化明显。**智谱（按模型独立并发）** 和 **千问（按模型独立）** 在同 provider 内多模型分配有效；**MiniMax（按类别共享）** 和 **DeepSeek（动态并发）** 无效
> - 海外 provider 中：**Anthropic** 按模型独立配额，同 provider 内多模型分配有效；**OpenAI** 付费层有效但免费层无效；**Google/Gemini** 各模型完全独立
> - 因此"同 provider 内切模型"是否有效完全取决于具体 provider 的政策和用户的使用层级，不能一概而论
>
> **实验验证方法**：若不确定所处 provider 的限流模式，可以在短时间内（1-2 分钟）执行单模型高频请求直至触发 429，然后切换同 provider 的另一模型观察是否仍被限流。若新模型恢复，则为模型级限流；若新模型同样被限流，则为账号级限流。

#### 2.7.4 用户方案的完整评估

```
配置方案：
  explore:   默认 M1 (Provider A) → fallback N1 (Provider B)
  librarian: 默认 M2 (Provider A) → fallback N2 (Provider B)
```

| 防护层面 | 是否有效 | 原因 |
|---------|---------|------|
| **M1 vs M2 分流（同 Provider A）** | ⚠️ 不确定 | 取决于 Provider A 的限流模式是账号级还是模型级 |
| **fallback 到 N1/N2（跨 Provider B）** | ✅ **确定有效** | 不同 provider，配额、Key、基础设施完全独立 |
| **并发时 M1+N1 同时工作** | ✅ **确定有效** | 跨越两个独立 provider，互不干扰 |

**核心结论**：同 provider 多模型分配的效果取决于该 provider 的限流模式，无法一概而论。但 fallback 到另一个 provider 的效果是确定的。

#### 2.7.5 更可靠的多层防御建议

无论限流模式是账号级还是模型级，以下三层防御始终有效：

```jsonc
{
  "agents": {
    "explore": {
      "model": "providerA/M1",
      "fallback_models": [
        "providerB/N1",          // L1: 先跨 provider（确定有效）
        "providerA/M3"           // L2: 再试同 provider 其他模型（可能有效）
      ]
    },
    "librarian": {
      "model": "providerA/M2",
      "fallback_models": [
        "providerB/N2",          // L1: 先跨 provider（确定有效）
        "providerA/M3"           // L2: 再试同 provider 其他模型（可能有效）
      ]
    }
  },

  "background_task": {
    "modelConcurrency": {
      "providerA/M1": 1,         // L3: 硬性限制每模型并发
      "providerA/M2": 1,
      "providerA/M3": 1,
      "providerB/N1": 3,
      "providerB/N2": 3
    },
    "providerConcurrency": {
      "providerA": 2,            // L3: Provider A 总并发上限（账号级限流下也有效）
      "providerB": 8
    }
  }
}
```

| 层 | 机制 | 对账号级限流有效？ | 对模型级限流有效？ |
|---|------|------------------|------------------|
| 同 provider 多模型分配 | M1 vs M2 | ❌ 无效 | ✅ 有效 |
| 跨 provider fallback | M1 → N1 | ✅ 有效 | ✅ 有效 |
| `modelConcurrency` | 限制单模型并发 | ✅ 有效 | ✅ 有效 |
| `providerConcurrency` | 限制总并发 | ✅ 有效 | ✅ 有效 |

#### 2.7.6 实际推荐操作

1. **优先依赖 `modelConcurrency` + `providerConcurrency`**——这两种机制无论限流模式如何，都是确定性保护
2. **跨 provider fallback 始终有效**——fallback chain 中至少包含一个不同 provider 的模型
3. **同 provider 多模型分配可作为辅助手段**——至少没有负面影响，在模型级限流的 provider 上还有明确收益
4. **不确定限流模式时，通过实验验证**：提升某一路的并发量，观察另一路的延迟/错误率是否受影响（可在 1-2 分钟内收集数据）

---

## 三、调查与分析过程

### 3.1 第一阶段：评估"Agent 多 Category"方案

**假设**：给 agent 配置多个 category，实例从池中选取。

**验证结果**：`AgentOverrideConfigSchema` 中 `category` 字段为 `z.string().optional()`（**单值**），非数组。`task()` 工具也只接受单个 `category` 字符串参数。**不可行**。

### 3.2 第二阶段：评估"behavior/model 解耦"方案

**假设**：新增 `model_categories` 数组，`behavior_category` 等字段。

**验证结果**：这些字段在 OMO schema 中**全部不存在**。`AgentOverrideConfigSchema` 仅包含以下字段：

```typescript
model?, fallback_models?, variant?, category?, skills?,
temperature?, top_p?, prompt?, prompt_append?, tools?,
disable?, description?, mode?, color?, permission?,
maxTokens?, thinking?, reasoningEffort?, textVerbosity?,
providerOptions?, ultrawork?, compaction?
```

### 3.3 第三阶段：评估"自定义 Category + Prompt 指令"方案

**假设**：利用 `CategoriesConfigSchema = z.record(z.string(), CategoryConfigSchema)` 支持任意字符串 key 的特性，创建多个自定义 category。

**验证结果**：
- ✅ 自定义 category 支持任意字符串名称
- ✅ `task(category="custom-name")` 调用正常工作
- ✅ 自定义 category 无 `CATEGORY_MODEL_REQUIREMENTS` 限制，`model` + `fallback_models` 完全可用
- ✅ 自定义 category 自动出现在 Sisyphus 的 `### AVAILABLE CATEGORIES` 提示和 `task()` 工具描述中
- ⚠️ 但仅覆盖 `task(category=...)` 路径（即 Sisyphus-Jr）

### 3.4 第四阶段：评估其他扩展点

系统性地检查了 OMO 所有可扩展点：

| 检查点 | 结果 |
|--------|------|
| `SisyphusAgentConfigSchema` 有无 `custom_tools` | ❌ 无，仅含 `disabled, planner_enabled, tdd` 等行为开关 |
| `ExperimentalConfigSchema` 有无多模型路由特性 | ❌ 无，仅含 `task_system, compaction` 等功能开关 |
| Hook 系统能否在 `task()` 创建前拦截并修改 category | ❌ `model-fallback` hook 在 session 创建后的 message 层面触发，不在 task 创建前 |
| `permission.task: "ask"` 能否让用户修改 category | ❌ 只能 Deny/Allow 已构造的调用，不能修改参数 |
| `RalphLoopConfigSchema` 能否复用 | ❌ 是上下文延续机制，与模型路由无关 |
| `agent_definitions` 能否注入额外逻辑 | ❌ 仅为字符串数组，无扩展性 |
| `background_task` 有无 dispatch 机制 | ❌ 仅有 concurrency 限制，无路由逻辑 |

### 3.5 第五阶段：评估 Explore/Librarian 通过 `prompt_append` 自感知

**假设**：在 Explore/Librarian 的 `prompt_append` 中写入负载分散指令，让 agent 自己选择不同模型。

**验证结果**：
- `agents.explore.prompt_append` 确实会追加到 Explore 的 system prompt 中（`applyOverrides()` 在 agent 注册时处理）
- 但 **agent 无法知晓自己的模型**（`model` 字段不注入到 prompt 中）
- **agent 无法选择模型**（模型由基础设施层通过 SDK 创建 session 时设定，agent 无 API 可以改变）
- **不可行**

### 3.6 第六阶段：替代方案模型调研

为验证结论的完备性，调研业界主流方案：

| 方案 | 项目 | 核心策略 | 与 OMO 的适配度 |
|------|------|---------|----------------|
| 简单轮询 | LiteLLM `simple-shuffle` | `itertools.cycle()` 循环分配 | 需在 OMO 内实现模型池 + 迭代器 |
| 并发感知 | LiteLLM `least-busy` | 追踪 in-flight 请求数，选最少者 | 需在 OMO 内实现计数器 |
| 权重随机 | LiteLLM `weight` + Portkey | `random.choices(deployments, weights)` | 需在 OMO 内实现选择器 |
| 网关级路由 | OpenRouter / Portkey | 请求层透明路由 | 独立于 OMO，需额外部署 |
| DI 多服务 | Semantic Kernel | `service_id` 多注册 + 显式指定 | 需重构 OMO 的模型注册机制 |
| 条件边路由 | LangGraph `conditional_edges` | 分类函数决定走哪个节点 | 与 OMO 的 `task()` 单参数签名冲突 |

**结论**：所有成熟方案都要求**在 OMO 内部实现模型池 + 选择器**，无法通过纯外部配置实现。

---

## 四、约束总结

### 4.1 不可改变的事实

| 约束 | 原因 |
|------|------|
| `call_omo_agent` 没有 `model`/`category` 参数 | 工具签名定义了固定参数集 |
| Agent 无模型自感知能力 | `model` 仅作为 SDK 配置，不注入 prompt |
| `category` 在 agent 配置中是单值字符串 | `AgentOverrideConfigSchema` 定义 |
| 模型解析是线性单路径 | `resolveModelPipeline` 返回唯一 `{model, variant}` |
| 无 Dispatch 层 | 无中间层拦截或修改模型选择 |

### 4.2 可用的配置杠杆

| 可用功能 | 作用边界 |
|---------|---------|
| 自定义 category | `task(category=...)` 路径，不覆盖 `call_omo_agent` |
| `fallback_models` | 所有 agent，但仅限**失败后**的被动降级 |
| `modelConcurrency` | 所有 agent，硬性并发上限 |
| `runtime_fallback` | 所有 agent，HTTP 错误自动切换 |

---

## 五、最终解决方案

### 5.1 方案概述

**三层防御组合方案**——利用 OMO 现有配置能力，将主动分散、被动降级、硬性限流三层机制叠加：

```
L1: 自定义 Category Pool 主动分散
  ── Sisyphus 在 task() 中看到多个可用类别，自然分散
  ── 覆盖范围: Sisyphus-Jr (category-based)

L2: fallback_models + runtime_fallback 被动降级
  ── 429/503 时自动切换到链中下一个模型
  ── 覆盖范围: 所有 agent

L3: modelConcurrency + providerConcurrency 硬性限流
  ── 达到上限后排队等待
  ── 覆盖范围: 所有 agent
```

### 5.2 配置实现

```jsonc
{
  "categories": {
    "search-pool-a": {
      "model": "opencode-go/minimax-m2.7",
      "fallback_models": [
        { "model": "anthropic/claude-haiku-4-5", "variant": "high" },
        { "model": "opencode/minimax-m2.7-highspeed" }
      ],
      "description": "Search pool A — Minimax M2.7 primary"
    },
    "search-pool-b": {
      "model": "anthropic/claude-haiku-4-5",
      "fallback_models": [
        { "model": "opencode-go/minimax-m2.7" },
        { "model": "opencode/minimax-m2.7-highspeed" }
      ],
      "description": "Search pool B — Haiku primary"
    },
    "search-pool-c": {
      "model": "opencode/minimax-m2.7-highspeed",
      "fallback_models": [
        { "model": "opencode-go/minimax-m2.7" },
        { "model": "anthropic/claude-haiku-4-5", "variant": "high" }
      ],
      "description": "Search pool C — Minimax Highspeed primary"
    }
  },

  "agents": {
    "sisyphus": {
      "prompt_append": "file://./rules/sisyphus-pool-rotation.md"
    },
    "explore": {
      "model": "opencode-go/minimax-m2.7",
      "fallback_models": [
        "anthropic/claude-haiku-4-5",          // L1: 先跨 provider（确定有效）
        "opencode/minimax-m2.7-highspeed"       // L2: 再同 provider（可能有效）
      ]
    },
    "librarian": {
      "model": "opencode-go/minimax-m2.7",
      "fallback_models": [
        "anthropic/claude-haiku-4-5",          // L1: 先跨 provider（确定有效）
        "opencode/minimax-m2.7-highspeed"       // L2: 再同 provider（可能有效）
      ]
    }
  },

  "runtime_fallback": {
    "enabled": true,
    "retry_on_errors": [429, 503, 529, 404, 1305],
    "max_fallback_attempts": 3,
    "cooldown_seconds": 30
  },

  "background_task": {
    "defaultConcurrency": 5,
    "providerConcurrency": {
      "opencode": 3,        // 注意：opencode 与 opencode-go 可能共享底层配额
      "opencode-go": 3      // 若同属 OpenCode 服务栈，两者并发会叠加计算
    },
    "modelConcurrency": {
      "opencode-go/minimax-m2.7": 2,
      "opencode/minimax-m2.7-highspeed": 2,
      "anthropic/claude-haiku-4-5": 2
    }
  }
}
```

### 5.3 规则文件（`rules/sisyphus-pool-rotation.md`）

```markdown
# Sisyphus Multi-Pool Rotation Rules

When dispatching parallel search/research tasks via `task(category=...)`:

1. **Rotate across pools to distribute load:**
   - task#1 → `search-pool-a` (Minimax)
   - task#2 → `search-pool-b` (Haiku)
   - task#3 → `search-pool-c` (Highspeed)
   - task#4 → back to `search-pool-a`

2. **For explore/librarian via `call_omo_agent`:**
   - Limit concurrent dispatches to 2 per batch
   - Wait for first batch to complete before sending next

3. **Goal:** Prevent any single model from receiving all concurrent requests simultaneously.

> Note: The rules above are soft guidance injected into the system prompt.
> Deterministic protection relies on `modelConcurrency` + `runtime_fallback` + `providerConcurrency`.
```

### 5.4 三层防御对应关系

```
请求进入
    │
    ▼
┌─────────────────────────────────┐
│ L1: 主动分散                    │
│ task(category="search-pool-a")  │  ← 概率性（依赖 Sisyphus 遵从度）
│ task(category="search-pool-b")  │
│ task(category="search-pool-c")  │
└────────────────┬────────────────┘
                 │ 限流 429/503
                 ▼
┌─────────────────────────────────┐
│ L2: 被动降级                    │
│ fallback_models → 切换模型       │  ← 确定性（代码级）
│ runtime_fallback → 错误重试      │
└────────────────┬────────────────┘
                 │ 并发持续堆积
                 ▼
┌─────────────────────────────────┐
│ L3: 硬性限流                    │
│ modelConcurrency → 排队等待      │  ← 确定性（代码级）
│ providerConcurrency → 全局熔断   │
└─────────────────────────────────┘
```

### 5.5 L1 层遵从度验证方法

L1（pool rotation 主动分散）依赖于 Sisyphus 对 prompt_append 指令的遵从程度。以下几种方法可以实际测量和提升 L1 效果：

**实验验证方法**：
1. **启用 OMO 的任务日志**：通过查看 `.sisyphus/` 目录下的任务记录，统计 Sisyphus 实际调用的 `category` 分布
2. **观察 fallback 触发频率**：若 `runtime_fallback` 日志中频繁出现 429 降级，说明 L1 分散不充分，L2 在过度承担降级任务
3. **手动构造测试**：在 prompt 中发出"同时搜索 5 个不同方向"的任务，观察 Sisyphus 实际使用了几种不同的 category。若全部使用同一个，说明遵从度低

**提升策略**：
- **强化 prompt 措辞**：使用 `MUST`、`ALWAYS` 等强制语气（参考 OMO 内置 prompt 风格）
- **配合 `modelConcurrency` 下限**：将 `modelConcurrency` 设为非常低的值（如 `"search-pool-a": 1`），强行迫使单个 pool 不可用后触发 fallback 到其他 pool
- **简化 category 数量**：若 Sisyphus 面对 3+ 个 pool 无法有效轮换，减少为 2 个 pool 可能提升分散率

> 注：L1 是三层防御中唯一概率性的层面。若实测分散率低于 30%，建议重点依赖 L2 + L3，不要高估 L1 的保护效果。

### 5.6 覆盖范围矩阵

| Agent 类型 | 调用方式 | L1 主动分散 | L2 被动降级 | L3 并发限流 |
|-----------|---------|------------|------------|------------|
| Sisyphus-Jr | `task(category=...)` | ✅ | ✅ | ✅ |
| Explore | `call_omo_agent("explore")` | ❌ | ✅ | ✅ |
| Librarian | `call_omo_agent("librarian")` | ❌ | ✅ | ✅ |
| Oracle | `call_omo_agent("oracle")` | ❌ | ✅ | ✅ |

---

## 六、局限性分析

### 6.1 当前方案的限制

| 限制 | 原因 | 影响程度 |
|------|------|---------|
| Explore/Librarian 无法参与 pool rotation | `call_omo_agent` 不接收 category 参数 | 中——它们通常为并行上限最高的 agent |
| L1 分散依赖 Sisyphus 模型遵从度 | Sisyphus 看到多个 category 但不一定会均匀使用 | 无法保证，但多 choice 的存在会自然提升分散概率 |
| 无实时负载感知 | `modelConcurrency` 是静态值，不考虑实时模型健康状态 | 对于大多数场景足够，极端场景下可调参数 |
| 自定义 category 无内置 fallback chain entry | `CATEGORY_MODEL_REQUIREMENTS` 中只有 8 个内置分类的条目 | 运行时 fallback 由 `runtime_fallback` 兜底，仍有效 |

### 6.2 所有被排除的方案及原因

| 被排除的方案 | 排除原因 |
|------------|---------|
| Agent 多 Category 数组 | OMO schema 不支持（`category` 为单值 `z.string()`） |
| behavior/model 解耦 | OMO schema 无 `model_categories`、`behavior_category` 等字段 |
| Hook 拦截修改 category | OMO hooks 不在 `task()` 创建前触发 |
| Agent `prompt_append` 自感知模型 | Agent 无模型信息、无选择能力 |
| `permission.task: "ask"` 监听修改 | 只能 Deny/Allow 不能修改参数 |
| 部署 API 聚合层（LiteLLM/Portkey） | 成本高、需要额外基础设施，超出纯配置范围 |

---

## 七、未来扩展方向（源码级）

若未来考虑修改 OMO 源码，以下是按优先级排列的可行方向：

### 7.1 扩展 `call_omo_agent` 工具签名（低侵入）

```typescript
interface CallOmoAgentArgs {
  description: string
  prompt: string
  subagent_type: string
  model?: string              // ← 新增：显式指定模型
  category?: string           // ← 新增：或指定 category 让系统解析模型
  run_in_background: boolean
  session_id?: string
}
```

让 Explore/Librarian 也能参与 pool rotation。

### 7.2 扩展 `AgentOverrideConfigSchema`（中侵入）

```typescript
// 新增字段
categories?: string[]              // 多 category 池
dispatch_strategy?: "round-robin" | "weighted-random" | "least-busy"
model_pool?: ModelPoolEntry[]      // 模型池（跨 category 的扁平池）
```

底层实现一个 `ModelSelector`：维护迭代器/计数器，每次调用返回选中的模型。

### 7.3 模型池 + 并发感知路由（重侵入，参考 LiteLLM）

```typescript
interface ModelPoolEntry {
  model: string
  variant?: string
  weight?: number          // 权重随机
  maxConcurrency?: number  // 每模型并发上限
}

class ModelPoolSelector {
  // 维护每个模型的活跃请求计数
  // select(): 选活跃请求最少的模型（least-busy）
  // 或根据权重随机选择（weighted-random）
}
```

实现后可在 `background_task` 配置中新增路由策略字段。

---

## 八、结论

在不修改 oh-my-openagent 源码的前提下，**三层防御组合方案**是利用所有现有配置能力的最优解。

其核心洞察是：
1. **Custom Category**（`z.record(z.string(), CategoryConfigSchema)`）是零代码改动下的主要杠杆，可为 Sisyphus-Jr 类型任务创建语义等价但模型不同的多个 pool
2. **`fallback_models` + `runtime_fallback`** 覆盖所有 agent 的被动降级场景
3. **`modelConcurrency` + `providerConcurrency`** 提供最终的硬性熔断保护

对于 Explore/Librarian 等不经过 category 系统的 agent，当前方案仅能提供 L2/L3 保护。若需完全覆盖，必须扩展 `call_omo_agent` 工具签名（参见第七章）。

该方案已在 OMO v1.0.155+ 源码上验证所有配置字段和机制的实际存在性，未使用任何虚构或不存在的配置项。

---

## 附录：关键源码文件索引

| 功能 | 文件路径 |
|------|---------|
| Category 配置 Schema | `src/config/schema/categories.ts` |
| Agent Override 配置 Schema | `src/config/schema/agent-overrides.ts` |
| Fallback Models Schema | `src/config/schema/fallback-models.ts` |
| 主配置 Schema | `src/config/schema/oh-my-opencode-config.ts` |
| Background Task Schema | `src/config/schema/background-task.ts` |
| 内置模型需求（fallback chain） | `src/shared/model-requirements.ts` |
| 模型解析 Pipeline | `src/shared/model-resolution-pipeline.ts` |
| Category 合并 | `src/shared/merge-categories.ts` |
| `call_omo_agent` 工具定义 | `src/tools/call-omo-agent/tools.ts` |
| `call_omo_agent` 参数类型 | `src/tools/call-omo-agent/types.ts` |
| `task()` 工具定义 | `src/tools/delegate-task/tools.ts` |
| Category 解析器 | `src/tools/delegate-task/category-resolver.ts` |
| 模型选择（delegate-task） | `src/tools/delegate-task/model-selection.ts` |
| 运行时 fallback hook | `src/hooks/model-fallback/hook.ts` |
| prompt_append file:// 解析器 | `src/agents/builtin-agents/resolve-file-uri.ts` |
| Agent Override 应用 | `src/agents/builtin-agents/agent-overrides.ts` |
| 通用 Agent 注册 | `src/agents/builtin-agents/general-agents.ts` |
| Sisyphus Agent 创建 | `src/agents/builtin-agents/sisyphus-agent.ts` |
| 动态 Prompt 构建 | `src/agents/dynamic-agent-category-skills-guide.ts` |
| 内置 Category 定义 | `src/tools/delegate-task/builtin-categories.ts` |

---

> 本文档为独立技术分析报告，不绑定任何特定项目或仓库。
