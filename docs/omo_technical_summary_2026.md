# Oh My OpenAgent (OMO) 技术总结报告
> 生成时间：2026 年 4 月 26 日  
> 适用场景：OpenCode 用户，多模型智能体编排，自动化开发任务  
> 项目地址：https://github.com/code-yeongyu/oh-my-openagent  
> 当前版本：1.0.155+（要求 OpenCode >= 1.0.150）

---

## 一、项目概览

### 1.1 核心理念（Manifesto）
OMO 不是“增强 Claude Code”，而是**打破单一模型限制**的编排系统：
- **目标**：将单个 AI 智能体转变为协调的开发团队，真正交付可生产的代码
- **原则**：
  - 人工干预是失败信号（Human Intervention = Bottleneck）
  - 代码应与高级工程师代码无法区分（Indistinguishable Code）
  - Token 成本 vs 生产力：高 Token 使用可接受，如果显著提升生产力
  - 最小化人类认知负载：人类只需表达“想要什么”，而非管理“怎么做”
  - 可预测、连续、可委托（像编译器一样工作）

### 1.2 系统定位
- **不是**：Claude Code 的插件或增强版
- **是**：跨模型编排层，自动选择最适合的智能体和模型
- **支持模型**：Claude（Opus/Sonnet/Haiku）、GPT（5.4/5.3-codex/5.4-mini）、Kimi K2.5、GLM-5/4.7-Flash、Gemini 3.1 Pro/Flash、MiniMax M2.7 等
- **不和任何供应商锁定**：支持 6+ 主流 AI 提供商

---

## 二、架构设计

### 2.1 三层编排架构

```
用户请求
    ↓
[意图门控] → 分类真实意图（研究/实现/修复/调查）
    ↓
[Sisyphus] → 主编排器，规划并委托给专家
    ├─→ [Prometheus] → 战略访谈式规划（Tab 键进入）
    ├─→ [Atlas] → Todo 编排和执行
    ├─→ [Oracle] → 架构咨询（只读）
    ├─→ [Librarian] → 文档/代码搜索
    ├─→ [Explore] → 快速代码库 grep
    └─→ [Category-based agents] → 按任务类型专业化
```

### 2.2 核心智能体

| 智能体 | 角色 | 默认模型链 | 特点 |
|--------|------|----------|------|
| **Sisyphus** | 主编排器（永不言弃） | anthropic\|github-copilot\|opencode/claude-opus-4-7(max) → opencode-go/kimi-k2.5 → openai\|github-copilot\|opencode/gpt-5.4(medium) → zai-coding-plan\|opencode/glm-5 | 规划、委托、驱动任务至完成，激进并行执行 |
| **Hephaestus** | 深度自主工作者（GPT 原生） | gpt-5.4(medium) only | 为 Codex 构建，“Amp on steroids”，需要 GPT 访问权限 |
| **Prometheus** | 战略规划器（访谈模式） | anthropic\|github-copilot\|opencode/claude-opus-4-7(max) → openai\|github-copilot\|opencode/gpt-5.4(high) | 像真正工程师一样访谈，生成详细计划 |
| **Atlas** | Todo 编排器 | anthropic\|github-copilot\|opencode/claude-sonnet-4-6 → opencode-go/kimi-k2.5 → openai\|github-copilot\|opencode/gpt-5.4(medium) | 执行 Prometheus 计划，分发任务给子智能体 |
| **Oracle** | 架构顾问（只读） | openai\|github-copilot\|opencode/gpt-5.4(high) → google\|github-copilot\|opencode/gemini-3.1-pro(high) | 处理架构决策和复杂调试 |
| **Metis** | 计划缺口分析器 | anthropic\|github-copilot\|opencode/claude-opus-4-7(max) → openai\|github-copilot\|opencode/gpt-5.4(high) | 在计划确定前捕获 Prometheus 遗漏的内容 |
| **Momus** | 无情审查器 | openai\|github-copilot\|opencode/gpt-5.4(xhigh) → anthropic\|github-copilot\|opencode/claude-opus-4-7(max) | 验证计划的清晰度、可验证性和完整性 |
| **Explore** | 快速代码库 grep | github-copilot\|xai/grok-code-fast-1 → opencode-go/minimax-m2.7-highspeed → opencode/minimax-m2.7 | 速度优先，使用快速模型 |
| **Librarian** | 文档/代码搜索 | opencode-go/minimax-m2.7 → opencode/minimax-m2.7-highspeed → anthropic\|opencode/claude-haiku-4-5 | 不需要深度推理，检索优先 |
| **Multimodal Looker** | 视觉/截图分析 | openai\|opencode/gpt-5.4(medium) → opencode-go/kimi-k2.5 → zai-coding-plan/glm-4.6v | GPT-5.4 现在引领默认视觉路径 |

### 2.3 关键机制

#### 意图门控（Intent Gate）
- Sisyphus 在响应任何请求前分类真实意图
- 避免误解，确保智能体理解上下文和真实目标

#### 智慧积累（Wisdom Accumulation）
- 每个任务后提取学习成果：惯例、成功、失败、注意事项、命令
- 传递给所有后续子智能体，防止重复错误
- 存储位置：`.sisyphus/notepads/{plan-name}/` 目录

#### 会话连续性（Session Continuity）
- `boulder.json` 跟踪活动计划和进度
- `/start-work` 自动恢复未完成的任务
- 跨会话保留上下文，计算进度（已检查 vs 未检查）

#### Hashline 编辑
- 使用 `LINE#ID` 内容哈希验证每次编辑
- 防止模型无法精确复现行导致的编辑失败
- 将 Grok Code Fast 1 成功率从 6.7% 提升到 68.3%

---

## 三、工作模式

### 3.1 Ultrawork 模式（懒人模式）
```
输入：ultrawork 或 ulw
过程：智能体自己探索代码库、研究模式、实现功能、验证诊断
结果：持续工作直到完成，无需人工逐步指导
适用：复杂任务、不想详细解释上下文的场景
```

### 3.2 Prometheus 模式（精确模式）
```
激活：按 Tab 键 → 选择 Prometheus，或输入 @plan "任务"
过程：访谈式规划 → 生成详细计划 → /start-work 执行
结果：精确、可验证的执行，适合多日项目、关键生产变更
适用：需要详细计划、决策追踪的复杂重构
```

### 3.3 任务分类系统（Category System）

**革命性创新**：智能体委托任务时不指定模型名称，而是指定**分类**：

| 分类 | 默认模型 | 用途 |
|------|----------|------|
| `visual-engineering` | google/gemini-3.1-pro(high) | 前端、UI/UX、设计、动画 |
| `ultrabrain` | openai/gpt-5.4(xhigh) | 深度逻辑推理、复杂架构决策 |
| `deep` | openai/gpt-5.4(medium) | 自主问题解决、彻底研究 |
| `artistry` | google/gemini-3.1-pro(high) | 创意/艺术创作、新颖想法 |
| `quick` | openai/gpt-5.4-mini | 琐碎任务、单文件修改、拼写修复 |
| `unspecified-low` | anthropic/claude-sonnet-4-6 | 不适合其他分类的一般任务（低努力） |
| `unspecified-high` | anthropic/claude-opus-4-7(max) | 不适合其他分类的一般任务（高努力） |
| `writing` | google/gemini-3-flash | 文档、散文、技术写作 |

**优势**：
- 右脑胜任右任务：Claude 善于遵循详细指令，GPT 善于原则驱动推理，Gemini 主导视觉任务
- 运行时自动映射到最优模型，无需手动切换

---

## 四、模型匹配系统

### 4.1 核心洞察：模型即开发者
不同模型有不同“大脑”，对相同指令理解完全不同：
- **Claude 系列**：响应机制驱动提示（详细检查清单、模板、逐步程序）
- **GPT 系列**：响应原则驱动提示（简洁原则、XML 标记结构）
- **Gemini**：视觉/前端任务表现突出
- **MiniMax/Kimi**：速度和智能的平衡

### 4.2 模型家族

| 家族 | 特点 | 代表模型 |
|------|------|----------|
| **Claude-like** | 指令遵循、结构化输出 | Claude Opus 4.7、Sonnet 4.6、Haiku 4.5、Kimi K2.5、GLM-5 |
| **GPT** | 显式推理、原则驱动 | GPT-5.4、GPT-5.3-codex、GPT-5.4-mini |
| **Different-Behavior** | 差异化推理风格 | Gemini 3.1 Pro、MiniMax M2.7、Grok Code Fast 1 |

### 4.3 智能体-模型匹配原则

**安全覆盖（同家族）**：
- Sisyphus：Opus → Sonnet、Kimi K2.5、GLM-5
- Prometheus：Opus → GPT-5.4（自动切换提示）

**危险覆盖（提示不支持）**：
- Sisyphus → 旧版 GPT 模型：**仍是错误匹配**
- Hephaestus → Claude：**无法复制 Codex 体验**
- Explore → Opus：**巨大的成本浪费**

### 4.4 模型解析优先级
1. UI 选中模型（用户手动选择）
2. 用户覆盖配置（config 中设置）
3. 分类默认模型（category 配置）
4. 用户 fallback_models（配置的回退链）
5. Provider fallback 链（内置回退）
6. 系统默认模型（OpenCode 配置）

---

## 五、安装与配置

### 5.1 快速安装
```bash
# 方法 1：交互式安装（推荐）
bunx oh-my-opencode install

# 方法 2：非交互式（指定订阅）
bunx oh-my-opencode install --no-tui \
  --claude=max20 --openai=yes --gemini=yes --copilot=no \
  --opencode-zen=yes --opencode-go=yes
```

### 5.2 订阅选项
| 选项 | 说明 |
|------|------|
| `--claude=no\|yes\|max20` | Claude Pro/Max 订阅 |
| `--openai=no\|yes` | ChatGPT Plus 订阅 |
| `--gemini=no\|yes` | Gemini 集成 |
| `--copilot=no\|yes` | GitHub Copilot 订阅 |
| `--opencode-zen=no\|yes` | OpenCode Zen 访问 |
| `--opencode-go=no\|yes` | OpenCode Go 订阅（$10/月） |
| `--zai-coding-plan=no\|yes` | Z.ai Coding Plan |
| `--kimi-for-coding=no\|yes` | Kimi for Coding |
| `--vercel-ai-gateway=no\|yes` | Vercel AI Gateway |

### 5.3 配置文件位置
- **项目配置**：`.opencode/oh-my-opencode.jsonc` 或 `.opencode/oh-my-opencode.json`
- **用户配置**：`~/.config/opencode/oh-my-opencode.jsonc`（macOS/Linux）或 `%APPDATA%\opencode\oh-my-opencode.jsonc`（Windows）

**重命名兼容性**：已发布包名仍为 `oh-my-opencode`，但 `opencode.json` 中插件注册优先使用 `oh-my-openagent`。

### 5.4 关键配置示例
```jsonc
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-openagent.schema.json",
  
  "agents": {
    "sisyphus": {
      "model": "kimi-for-coding/k2p5",
      "ultrawork": { "model": "anthropic/claude-opus-4-7", "variant": "max" }
    },
    "oracle": { "model": "openai/gpt-5.4", "variant": "high" }
  },

  "categories": {
    "visual-engineering": {
      "model": "google/gemini-3.1-pro",
      "variant": "high"
    },
    "quick": { "model": "openai/gpt-5.4-mini" }
  },

  "background_task": {
    "providerConcurrency": {
      "anthropic": 3,
      "openai": 3,
      "opencode": 10
    }
  },

  "runtime_fallback": {
    "enabled": true,
    "retry_on_errors": [400, 429, 503, 529],
    "max_fallback_attempts": 3,
    "timeout_seconds": 30
  }
}
```

---

## 六、CLI 命令参考

| 命令 | 描述 |
|------|------|
| `install` | 交互式安装向导 |
| `doctor` | 环境诊断和健康检查（检查系统、配置、工具、模型） |
| `run <message>` | 带 Todo/后台任务完成强制的 OpenCode 会话运行 |
| `get-local-version` | 显示本地版本信息和更新检查 |
| `refresh-model-capabilities` | 刷新缓存的 models.dev 模型能力数据 |
| `version` | 显示版本信息 |
| `mcp oauth` | MCP OAuth 认证管理 |

### doctor 诊断类别
```bash
bunx oh-my-opencode doctor --verbose  # 详细诊断
bunx oh-my-opencode doctor --status   # 紧凑系统仪表盘
bunx oh-my-opencode doctor --json     # JSON 输出（CI 环境）
```

输出示例：
```
✓ OpenCode version: 1.0.155 (>= 1.0.150)
✓ Plugin registered in opencode.json
✓ oh-my-opencode.jsonc is valid
✓ Model resolution: all agents have valid fallback chains
⚠ categories.visual-engineering: using default model
Summary: 10 passed, 1 warning, 0 failed
```

---

## 七、功能特性

### 7.1 Skills（技能系统）
内置技能：`playwright`、`playwright-cli`、`agent-browser`、`dev-browser`、`git-master`、`frontend-ui-ux`

**自定义技能**：在 `.opencode/skills/` 或 `~/.config/opencode/skills/` 下创建 `SKILL.md`

示例：`.opencode/skills/my-skill/SKILL.md`
```markdown
---
name: my-skill
description: My special custom skill
mcp:
  my-mcp:
    command: npx
    args: ["-y", "my-mcp-server"]
---
# My Skill Prompt
This content will be injected into the agent's system prompt.
```

### 7.2 Hooks（钩子系统）
内置钩子：`todo-continuation-enforcer`、`context-window-monitor`、`session-recovery`、`session-notification`、`comment-checker`、`grep-output-truncator` 等

禁用特定钩子：
```json
{ "disabled_hooks": ["comment-checker", "start-work"] }
```

### 7.3 任务系统（experimental）
需要启用：`{ "experimental": { "task_system": true } }`

**Task Schema**：
```typescript
interface Task {
  id: string;           // T-{uuid}
  subject: string;       // 命令式："Run tests"
  status: "pending" | "in_progress" | "completed" | "deleted";
  blockedBy: string[];   // 阻塞此任务的 ID 列表
  owner?: string;       // 智能体名称
  threadID: string;      // 会话 ID（自动设置）
}
```

**并行执行与依赖**：
```
[Build Frontend] ──┐
                      ├──→ [Integration Tests] ──→ [Deploy]
[Build Backend]  ──┘
```
- `blockedBy: []` 的任务并行运行
- 依赖任务在阻塞者完成前等待

### 7.4 浏览器自动化
| 提供商 | 接口 | 安装 |
|--------|------|------|
| `playwright`（默认） | MCP 工具 | 通过 npx 自动安装 |
| `agent-browser` | Bash CLI | `bun add -g agent-browser && agent-browser install` |

切换提供商：
```json
{ "browser_automation_engine": { "provider": "agent-browser" } }
```

### 7.5 LSP 集成
```json
{
  "lsp": {
    "typescript-language-server": {
      "command": ["typescript-language-server", "--stdio"],
      "extensions": [".ts", ".tsx"],
      "priority": 10
    },
    "pylsp": { "disabled": true }
  }
}
```

---

## 八、故障排除

### 8.1 Ollama 流式问题
**错误**：`JSON Parse error: Unexpected EOF`

**原因**：Ollama 返回 NDJSON（换行分隔的 JSON），Claude Code SDK 期望单个 JSON 对象

**解决方案**：
```json
{
  "agents": {
    "explore": { "model": "ollama/qwen3-coder", "stream": false }
  }
}
```

### 8.2 常见问答
| 问题 | 解决方案 |
|------|----------|
| 切换到 Prometheus 但没反应 | Prometheus 默认进入访谈模式，回答它的问题，然后说“make it a plan” |
| /start-work 说“no active plan found” | 在 `.sisyphus/plans/` 下创建计划，或删除 `.sisyphus/boulder.json` 重试 |
| 想从 Atlas 切回正常模式 | 输入 `exit` 或启动新会话，Atlas 通过 `/start-work` 进入 |
| Hephaestus 还是 Sisyphus+ulw？ | 90% 任务用 `ulw`；需要 GPT-5.4 深度推理时用 Hephaestus |
| 看到“Using legacy package name”警告 | 更新 `opencode.json` 插件条目从 `"oh-my-opencode"` 到 `"oh-my-openagent"` |

### 8.3 诊断命令
```bash
# 检查 OMO 状态
bunx oh-my-opencode doctor --verbose

# 查看模型解析
opencode models

# 查看当前配置
cat ~/.config/opencode/oh-my-opencode.jsonc
```

---

## 九、与传统工具对比

| 特性 | Claude Code | OMO（Oh My OpenAgent） |
|------|-------------|------------------------|
| **执行方式** | 单智能体、单模型 | 协调团队、多模型编排 |
| **并行执行** | ❌ 一次处理一件事 | ✅ 同时启动 5+ 后台智能体 |
| **模型选择** | 手动切换 | 按任务类型自动路由到最优模型 |
| **上下文管理** | 单模型上下文窗口 | 智能体分工、智慧积累、上下文修剪 |
| **Hashline 编辑** | ❌ 模型无法复现行时失败 | ✅ `LINE#ID` 哈希验证，零过期编辑错误 |
| **会话连续性** | 关闭即丢失 | ✅ `boulder.json` 跟踪，跨会话恢复 |
| **Skills** | ❌ 无 | ✅ 技能系统，带嵌入式 MCP |
| **LSP 工具** | ❌ 无 | ✅ 工作区重命名、跳转定义、查找引用、预构建诊断 |
| **约束执行** | ❌ 智能体可以偷懒 | ✅ Todo 强制器、评论检查器、Ralph 循环 |

---

## 十、总结与建议

### 10.1 核心优势
1. **真正多模型编排**：不是简单的模型切换，而是根据任务类型自动选择最优“大脑”
2. **会话连续性**：`/start-work` 和 `boulder.json` 实现跨会话任务恢复
3. **并行执行能力**：5+ 智能体同时工作，研究、实现、验证同步进行
4. **智慧积累系统**：避免重复错误，惯例自动传递
5. **强大的回退机制**：`runtime_fallback` 支持按错误类型、模型链、超时自动切换

### 10.2 适用场景
- ✅ 复杂多日项目，需要精确规划和执行
- ✅ 需要同时使用多个 AI 提供商（Claude + GPT + Gemini）
- ✅ 希望“委托任务后不管”，智能体自主完成
- ✅ 需要会话连续性，跨多天项目跟踪进度
- ✅ 想要避免单一模型锁定，灵活利用各模型优势

### 10.3 不适用场景
- ❌ 简单单文件修改（直接用 OpenCode 更简单）
- ❌ 没有 Claude/GPT 订阅（免费层功能受限）
- ❌ 不想配置多个提供商（配置复杂度较高）

### 10.4 推荐配置组合
```jsonc
{
  "runtime_fallback": { "enabled": true },
  "background_task": {
    "defaultConcurrency": 5,
    "providerConcurrency": { "anthropic": 3, "openai": 3 }
  },
  "experimental": { "task_system": true },
  "sisyphus_agent": { "planner_enabled": true }
}
```

---
> 报告数据来源：https://github.com/code-yeongyu/oh-my-openagent/tree/dev/docs/ 全量文档（manifesto.md、guide/、reference/、troubleshooting/、superpowers/、examples/）
> 报告生成：基于官方文档的客观技术总结，未添加主观评价
