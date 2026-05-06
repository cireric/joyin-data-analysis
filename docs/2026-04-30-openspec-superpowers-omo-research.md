# OpenSpec、SuperPowers、oh-my-openagent 调研报告

> 调研日期：2026-04-30
> 调研目的：了解三个 AI Coding Agent 增强工具的功能、适用场景、社区评价，以及组合使用的可行性分析

---

## 目录

1. [概述](#概述)
2. [OpenSpec 详解](#openspec-详解)
3. [SuperPowers 详解](#superpowers-详解)
4. [oh-my-openagent 详解](#oh-my-openagent-详解)
5. [功能对比矩阵](#功能对比矩阵)
6. [组合使用分析](#组合使用分析)
7. [社区评价汇总](#社区评价汇总)
8. [结论与建议](#结论与建议)

---

## 概述

这三个项目都是为 AI Coding Agent（如 Claude Code、OpenCode、Cursor 等）提供增强功能的工具，但它们的定位和侧重点各有不同：

| 项目 | 定位 | 核心价值 | GitHub Stars |
|------|------|----------|--------------|
| **OpenSpec** | Spec-Driven Development 框架 | 规格驱动开发，需求文档持久化 | 44.1k |
| **SuperPowers** | 软件开发方法论 + Skills 系统 | TDD、系统化流程、最佳实践 | 较新 |
| **oh-my-openagent** | Agent Harness（代理框架） | 多模型编排、并行执行、工具集成 | 55.1k |

---

## OpenSpec 详解

### 基本信息

- **官网**: https://openspec.dev
- **GitHub**: https://github.com/Fission-AI/OpenSpec
- **Stars**: 44.1k
- **Forks**: 3.1k
- **许可证**: MIT
- **支持工具**: 25+ AI Coding Tools（Claude Code, Cursor, Codex, GitHub Copilot, OpenCode, Windsurf, Gemini CLI 等）

### 核心理念

```
→ fluid not rigid        （流动而非僵化）
→ iterative not waterfall（迭代而非瀑布）
→ easy not complex       （简单而非复杂）
→ built for brownfield not just greenfield（为棕地项目设计，不只是绿地项目）
→ scalable from personal projects to enterprises（从个人项目到企业级可扩展）
```

### 核心功能

#### 1. Spec-Driven Development (SDD)

OpenSpec 的核心是**规格驱动开发**。每个功能变更都会生成一个完整的变更提案文件夹：

```
openspec/changes/add-dark-mode/
├── proposal.md    ← 为什么做这个，改什么
├── specs/         ← 需求和场景
├── design.md      ← 技术决策
└── tasks.md       ← 实现任务清单
```

#### 2. Spec Delta（规格增量）

每次变更产生 spec delta，捕获系统需求的变化：

```markdown
### Requirement: Session expiration
- The system SHALL expire sessions after a configured duration.
+ The system SHALL support configurable session expiration periods.

#### Scenario: Default session timeout
- GIVEN a user has authenticated
- - WHEN 24 hours pass without activity
+ - WHEN 24 hours pass without "Remember me"
- THEN invalidate the session token
```

#### 3. 持久化上下文

规格文件存储在代码库中，与代码一起版本控制：

```
openspec/specs/
├── auth-login/
│   └── spec.md
├── auth-session/
│   └── spec.md
└── checkout-payment/
    └── spec.md
```

### 工作流程

```
/opsx:propose "your idea"  →  创建提案
         ↓
/opsx:apply               →  实现任务
         ↓
/opsx:archive             →  归档变更
```

### 主要命令

| 命令 | 功能 |
|------|------|
| `/opsx:propose` | 创建新的变更提案 |
| `/opsx:apply` | 执行实现任务 |
| `/opsx:archive` | 归档已完成的变更 |
| `/opsx:new` | 新工作流（扩展模式） |
| `/opsx:continue` | 继续工作流 |
| `/opsx:verify` | 验证实现 |
| `/opsx:sync` | 同步规格 |

### 适用场景

1. **团队协作**：规格文档可共享、可审查
2. **长期项目**：需求文档持久化，不随会话消失
3. **复杂系统**：棕地项目，需要理解现有系统
4. **多会话开发**：跨多个对话保持一致性
5. **Code Review**：审查意图而非仅代码

### 与竞品对比

| 对比项 | OpenSpec | Spec Kit (GitHub) | Kiro (AWS) |
|--------|----------|-------------------|------------|
| 重量级 | 轻量 | 重量级 | 中等 |
| 阶段门控 | 无刚性门控 | 有刚性阶段门控 | 有 |
| 设置复杂度 | 简单 (npm install) | 复杂 (Python setup) | 需要特定 IDE |
| 工具兼容性 | 25+ 工具 | GitHub 生态 | AWS IDE 锁定 |
| 棕地支持 | 优秀 | 一般 | 一般 |

---

## SuperPowers 详解

### 基本信息

- **GitHub**: https://github.com/obra/superpowers
- **作者**: Jesse Vincent (Prime Radiant)
- **许可证**: MIT
- **支持平台**: Claude Code, OpenAI Codex, Cursor, OpenCode, GitHub Copilot CLI, Gemini CLI

### 核心理念

SuperPowers 是一套**完整的软件开发方法论**，通过可组合的 Skills 系统实现：

> "It starts from the moment you fire up your coding agent. As soon as it sees that you're building something, it *doesn't* just jump into trying to write code. Instead, it steps back and asks you what you're really trying to do."

### 核心工作流程

```
1. brainstorming      → 理解需求，探索方案，生成设计文档
2. using-git-worktrees → 创建隔离工作区
3. writing-plans      → 分解任务，生成实现计划
4. subagent-driven-development → 并行执行任务
5. test-driven-development → RED-GREEN-REFACTOR 循环
6. requesting-code-review → 代码审查
7. finishing-a-development-branch → 合并/PR 决策
```

### Skills 库

#### 测试类
- **test-driven-development**: RED-GREEN-REFACTOR 循环，包含测试反模式参考

#### 调试类
- **systematic-debugging**: 4 阶段根因分析流程
- **verification-before-completion**: 确保真正修复

#### 协作类
- **brainstorming**: 苏格拉底式设计细化
- **writing-plans**: 详细实现计划
- **executing-plans**: 批量执行 + 检查点
- **dispatching-parallel-agents**: 并发子代理工作流
- **requesting-code-review**: 审查前检查清单
- **receiving-code-review**: 响应反馈
- **using-git-worktrees**: 并行开发分支
- **finishing-a-development-branch**: 合并/PR 决策工作流
- **subagent-driven-development**: 两阶段审查（规格合规 + 代码质量）

#### 元类
- **writing-skills**: 创建新 Skills
- **using-superpowers**: Skills 系统介绍

### 设计哲学

1. **Test-Driven Development** - 先写测试，始终如此
2. **Systematic over ad-hoc** - 流程优于猜测
3. **Complexity reduction** - 简单性为首要目标
4. **Evidence over claims** - 验证后再声明成功

### 安装方式

```bash
# Claude Code Official Marketplace
/plugin install superpowers@claude-plugins-official

# OpenCode
# 告诉 OpenCode:
Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md
```

### 适用场景

1. **严肃的软件开发**：需要系统化流程
2. **TDD 实践者**：强制测试驱动
3. **团队协作**：代码审查、分支管理
4. **复杂项目**：需要设计文档和实现计划
5. **质量优先**：验证机制确保质量

---

## oh-my-openagent 详解

### 基本信息

- **官网**: https://ohmyopenagent.com
- **GitHub**: https://github.com/code-yeongyu/oh-my-openagent
- **作者**: code-yeongyu
- **Stars**: 55.1k
- **Forks**: 4.5k
- **许可证**: SUL-1.0
- **支持平台**: OpenCode（主要）、Claude Code 兼容

### 核心定位

> "If OpenCode is Debian/Arch, OmO is Ubuntu/Omarchy."

oh-my-openagent (OmO) 是一个**Agent Harness（代理框架）**，提供多模型编排、并行执行、工具集成等核心能力。

### 核心特性

#### 1. Discipline Agents（纪律代理）

| 代理 | 模型 | 角色 |
|------|------|------|
| **Sisyphus** | claude-opus-4-7 / kimi-k2.5 / glm-5 | 主编排器，不停止直到完成 |
| **Hephaestus** | gpt-5.4 | 自主深度工作者，端到端执行 |
| **Prometheus** | claude-opus-4-7 / kimi-k2.5 / glm-5 | 战略规划师，面试模式 |
| **Oracle** | - | 架构/调试 |
| **Librarian** | - | 文档/代码搜索 |
| **Explore** | - | 快速代码库搜索 |

#### 2. ultrawork 命令

```bash
ultrawork  # 或 ulw
```

一个命令激活所有代理，不停止直到任务完成。

#### 3. Agent Orchestration（代理编排）

代理不直接选择模型，而是选择**类别**，系统自动映射到合适的模型：

| 类别 | 用途 |
|------|------|
| `visual-engineering` | 前端、UI/UX、设计 |
| `deep` | 自主研究 + 执行 |
| `quick` | 单文件修改、拼写错误 |
| `ultrabrain` | 困难逻辑、架构决策 |

#### 4. Hash-Anchored Edit Tool（哈希锚定编辑工具）

解决 "Harness Problem"（框架问题）：

```
11#VK| function hello() {
22#XJ|   return "world";
33#MB| }
```

每行带有内容哈希，编辑时验证哈希，防止过时行错误。

#### 5. 内置 MCP 服务器

- **Exa**: 网页搜索
- **Context7**: 官方文档
- **Grep.app**: GitHub 代码搜索

#### 6. 其他特性

- **LSP + AST-Grep**: IDE 级精度
- **Tmux 集成**: 交互式终端
- **Claude Code 兼容**: 所有 hooks、commands、skills、MCPs、plugins 都可用
- **Skill-Embedded MCPs**: Skills 自带 MCP 服务器
- **Ralph Loop**: 自引用循环，直到 100% 完成
- **Todo Enforcer**: 代理空闲时强制拉回
- **Comment Checker**: 检查 AI 生成的注释质量
- **/init-deep**: 自动生成层级 AGENTS.md 文件

### 安装方式

```bash
# 让 LLM Agent 安装
curl -s https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/refs/heads/dev/docs/guide/installation.md
```

### 适用场景

1. **多模型编排**：需要组合不同模型的优势
2. **大规模重构**：并行执行，高效处理
3. **成本优化**：使用 ChatGPT/Kimi/GLM 等低成本方案
4. **OpenCode 用户**：深度集成，最佳体验
5. **快速开发**：ultrawork 一键完成

### 社区评价摘录

> "It made me cancel my Cursor subscription. Unbelievable things are happening in the open source community." - Arthur Guiot

> "If Claude Code does in 7 days what a human does in 3 months, Sisyphus does it in 1 hour." - B, Quant Researcher

> "Knocked out 8000 eslint warnings with Oh My Opencode, just in a day" - Jacob Ferrari

> "I converted a 45k line tauri app into a SaaS web app overnight using Ohmyopencode and ralph loop." - James Hargis

---

## 功能对比矩阵

### 核心定位对比

| 维度 | OpenSpec | SuperPowers | oh-my-openagent |
|------|----------|-------------|-----------------|
| **主要定位** | 规格驱动开发框架 | 软件开发方法论 | Agent Harness |
| **核心价值** | 需求文档持久化 | TDD + 系统化流程 | 多模型编排 + 并行执行 |
| **抽象层级** | 需求层 | 流程层 | 执行层 |
| **主要用户** | 团队、长期项目 | 严肃开发者 | OpenCode 用户、效率优先 |

### 功能覆盖对比

| 功能 | OpenSpec | SuperPowers | oh-my-openagent |
|------|:--------:|:-----------:|:---------------:|
| **需求管理** | ✅ 核心 | ⚠️ brainstorming | ⚠️ Prometheus |
| **设计文档** | ✅ design.md | ✅ specs | ⚠️ 部分 |
| **任务分解** | ✅ tasks.md | ✅ writing-plans | ✅ ultrawork |
| **TDD 流程** | ❌ | ✅ 核心 | ⚠️ 部分 |
| **代码审查** | ⚠️ spec review | ✅ requesting-code-review | ⚠️ 部分 |
| **多模型编排** | ❌ | ❌ | ✅ 核心 |
| **并行执行** | ❌ | ✅ subagent-driven | ✅ Background Agents |
| **MCP 集成** | ❌ | ❌ | ✅ 内置 |
| **LSP 工具** | ❌ | ❌ | ✅ |
| **Git Worktrees** | ❌ | ✅ | ❌ |
| **调试流程** | ❌ | ✅ systematic-debugging | ⚠️ Oracle |
| **规格持久化** | ✅ 核心 | ⚠️ 设计文档 | ❌ |
| **跨会话上下文** | ✅ | ❌ | ❌ |
| **团队协作** | ✅ 强 | ⚠️ 中等 | ⚠️ 中等 |

### 工具兼容性对比

| 工具 | OpenSpec | SuperPowers | oh-my-openagent |
|------|:--------:|:-----------:|:---------------:|
| Claude Code | ✅ | ✅ | ✅ 兼容 |
| OpenCode | ✅ | ✅ | ✅ 原生 |
| Cursor | ✅ | ✅ | ⚠️ 部分 |
| GitHub Copilot | ✅ | ✅ | ⚠️ 部分 |
| Gemini CLI | ✅ | ✅ | ⚠️ 部分 |
| Codex | ✅ | ✅ | ⚠️ 部分 |
| Windsurf | ✅ | ❌ | ❌ |

---

## 组合使用分析

### 组合一：OpenSpec + SuperPowers

#### 功能重叠分析

| 功能 | OpenSpec | SuperPowers | 重叠程度 |
|------|----------|-------------|----------|
| 需求细化 | `/opsx:propose` | `brainstorming` | 🔴 高 |
| 设计文档 | `design.md` | `specs/` | 🔴 高 |
| 任务分解 | `tasks.md` | `writing-plans` | 🔴 高 |
| 代码审查 | spec review | `requesting-code-review` | 🟡 中 |

#### 协作可行性

**优势**：
- OpenSpec 提供持久化的规格管理
- SuperPowers 提供严格的 TDD 流程
- 可以互补：OpenSpec 管需求，SuperPowers 管实现

**挑战**：
- 两个系统都有"设计文档"和"任务分解"，容易冲突
- 工作流不一致：OpenSpec 用 slash commands，SuperPowers 用 skills 自动触发
- 用户需要理解两套术语和流程

#### 推荐工作流

```
OpenSpec (需求阶段)          SuperPowers (实现阶段)
     │                            │
/opsx:propose ──────────────→ brainstorming
     │                            │
proposal.md                   设计文档
specs/                        specs/
design.md         ──────────→ writing-plans
     │                            │
tasks.md                      实现计划
     │                            │
     └──────────────────────→ TDD 执行
                                   │
                            requesting-code-review
                                   │
                            finishing-a-development-branch
```

**结论**：⚠️ 可组合但需要明确分工，建议 OpenSpec 负责需求管理，SuperPowers 负责实现流程。

---

### 组合二：SuperPowers + oh-my-openagent

#### 功能重叠分析

| 功能 | SuperPowers | oh-my-openagent | 重叠程度 |
|------|-------------|-----------------|----------|
| 并行执行 | subagent-driven | Background Agents | 🔴 高 |
| 任务分解 | writing-plans | Prometheus | 🔴 高 |
| 调试 | systematic-debugging | Oracle | 🟡 中 |
| 代码审查 | requesting-code-review | 部分 | 🟢 低 |

#### 协作可行性

**优势**：
- oh-my-openagent 提供强大的多模型编排能力
- SuperPowers 提供系统化的开发方法论
- oh-my-openagent 兼容 Claude Code 生态，SuperPowers 的 skills 可以工作

**挑战**：
- 两者都有"并行代理执行"，可能冲突
- oh-my-openagent 的 `ultrawork` 可能绕过 SuperPowers 的流程
- SuperPowers 的 TDD 强制可能与 oh-my-openagent 的快速执行冲突

**关键问题**：
- oh-my-openagent 的 `ultrawork` 是"一键完成"模式
- SuperPowers 强调"先设计后实现"
- 两者理念有冲突

#### 推荐配置

如果同时使用，建议：

1. **禁用 oh-my-openagent 的自动模式**，保留其工具能力
2. **使用 SuperPowers 的流程**，但利用 oh-my-openagent 的 MCP 和 LSP 工具
3. **明确分工**：
   - SuperPowers: 流程控制、TDD、审查
   - oh-my-openagent: 工具支持、多模型路由

**结论**：⚠️ 可组合但理念有冲突，需要选择主导方。建议以 SuperPowers 流程为主，oh-my-openagent 作为工具层。

---

### 组合三：OpenSpec + oh-my-openagent

#### 功能重叠分析

| 功能 | OpenSpec | oh-my-openagent | 重叠程度 |
|------|----------|-----------------|----------|
| 需求管理 | 核心 | Prometheus | 🟡 中 |
| 任务分解 | tasks.md | ultrawork | 🟡 中 |
| 规格持久化 | 核心 | ❌ | 🟢 无重叠 |
| 多模型编排 | ❌ | 核心 | 🟢 无重叠 |

#### 协作可行性

**优势**：
- 功能互补性强：OpenSpec 管需求，oh-my-openagent 管执行
- 无重大功能重叠
- OpenSpec 的规格可以作为 oh-my-openagent 的上下文

**挑战**：
- 工作流需要手动衔接
- oh-my-openagent 的快速执行可能忽略 OpenSpec 的规格

#### 推荐工作流

```
OpenSpec (需求管理)          oh-my-openagent (执行)
     │                            │
/opsx:propose                     │
     │                            │
proposal.md                       │
specs/                            │
design.md                         │
     │                            │
tasks.md  ──────────────────→ ultrawork
     │                            │
     │                      多模型并行执行
     │                            │
/opsx:archive                     │
     │                            │
规格更新 ←─────────────────── 实现完成
```

**结论**：✅ 推荐组合。功能互补，重叠少，可以形成"需求管理 + 高效执行"的完整流程。

---

### 组合四：OpenSpec + SuperPowers + oh-my-openagent

#### 三者关系图

```
                    ┌─────────────┐
                    │  OpenSpec   │
                    │ (需求层)    │
                    └──────┬──────┘
                           │
                    规格文档持久化
                           │
                           ▼
              ┌────────────────────────┐
              │     SuperPowers        │
              │    (流程层)            │
              │                        │
              │  TDD + 系统化方法论    │
              └───────────┬────────────┘
                          │
                    流程控制
                          │
                          ▼
              ┌────────────────────────┐
              │   oh-my-openagent      │
              │    (执行层)            │
              │                        │
              │  多模型编排 + 工具集成  │
              └────────────────────────┘
```

#### 功能分工建议

| 层级 | 工具 | 职责 |
|------|------|------|
| **需求层** | OpenSpec | 需求收集、规格文档、变更管理 |
| **流程层** | SuperPowers | TDD 流程、代码审查、分支管理 |
| **执行层** | oh-my-openagent | 多模型编排、工具调用、并行执行 |

#### 完整工作流

```
1. 需求阶段 (OpenSpec)
   /opsx:propose "feature"
   → proposal.md, specs/, design.md, tasks.md

2. 设计阶段 (SuperPowers)
   brainstorming → 验证设计
   writing-plans → 实现计划

3. 实现阶段 (SuperPowers + oh-my-openagent)
   TDD 循环:
   - test-driven-development (流程)
   - oh-my-openagent 工具 (执行)

4. 审查阶段 (SuperPowers)
   requesting-code-review
   verification-before-completion

5. 完成阶段 (OpenSpec + SuperPowers)
   /opsx:archive (OpenSpec)
   finishing-a-development-branch (SuperPowers)
```

#### 挑战与风险

1. **复杂度高**：三套系统，学习成本大
2. **流程冲突**：三者都有"任务分解"，需要明确主次
3. **维护成本**：三个项目独立演进，兼容性需持续关注
4. **过度工程**：对于大多数项目，可能过度设计

#### 适用场景

**推荐使用三合一组合的场景**：
- 大型团队项目
- 长期维护的复杂系统
- 对质量和流程有严格要求
- 需要多模型编排降低成本

**不推荐的场景**：
- 小型项目
- 快速原型开发
- 个人项目
- 简单任务

**结论**：⚠️ 可行但复杂度高，仅推荐大型团队项目使用。大多数情况下，选择 1-2 个工具即可。

---

## 社区评价汇总

### OpenSpec 社区评价

**正面评价**：
- "轻量级，不引入繁重的流程"
- "规格持久化解决了 AI 会话上下文丢失的问题"
- "支持 25+ 工具，不锁定特定平台"
- "棕地项目友好，不需要从头开始"

**负面/改进建议**：
- "需要主动维护规格文档，有一定学习成本"
- "对于 vibe coder 来说可能太正式"
- "团队协作功能还在开发中"

### SuperPowers 社区评价

**正面评价**：
- "TDD 强制让代码质量显著提升"
- "系统化流程减少了猜测和返工"
- "skills 自动触发，无需记忆命令"
- "代码审查流程完善"

**负面/改进建议**：
- "流程较重，不适合快速迭代"
- "学习曲线较陡"
- "与快速执行类工具理念冲突"

### oh-my-openagent 社区评价

**正面评价**：
- "取消了 Cursor 订阅" - Arthur Guiot
- "Claude Code 7 天的工作，Sisyphus 1 小时完成"
- "一天清理了 8000 个 eslint 警告" - Jacob Ferrari
- "一夜之间把 45k 行 Tauri 应用转成 SaaS Web 应用" - James Hargis
- "用了就回不去了" - d0t3ch
- "开发体验达到了完全不同的维度" - 苔硯:こけすずり

**负面/改进建议**：
- "配置较复杂，建议让 AI 安装"
- "主要针对 OpenCode，其他平台支持有限"
- "Anthropic 封禁了 OpenCode（因为 OmO 太强）"

---

## 结论与建议

### 工具选择建议

| 场景 | 推荐工具 | 理由 |
|------|----------|------|
| **团队协作 + 长期项目** | OpenSpec | 规格持久化，支持跨会话协作 |
| **质量优先 + TDD 实践** | SuperPowers | 强制 TDD，系统化流程 |
| **效率优先 + OpenCode 用户** | oh-my-openagent | ultrawork 一键完成，多模型编排 |
| **成本优化** | oh-my-openagent | 支持 ChatGPT/Kimi/GLM 等低成本方案 |
| **大型团队项目** | OpenSpec + SuperPowers + oh-my-openagent | 完整的需求-流程-执行链 |
| **个人项目/快速原型** | oh-my-openagent 或 SuperPowers（二选一） | 避免过度工程 |

### 组合使用建议

| 组合 | 推荐度 | 说明 |
|------|:------:|------|
| **OpenSpec + oh-my-openagent** | ✅ 推荐 | 功能互补，重叠少 |
| **OpenSpec + SuperPowers** | ⚠️ 可行 | 需明确分工，OpenSpec 管需求，SuperPowers 管实现 |
| **SuperPowers + oh-my-openagent** | ⚠️ 可行 | 理念有冲突，需选择主导方 |
| **三合一** | ⚠️ 谨慎 | 复杂度高，仅适合大型团队项目 |

### 最终建议

1. **对于 OpenCode 用户**：
   - 首选 **oh-my-openagent**（原生支持，最佳体验）
   - 如需规格管理，可叠加 **OpenSpec**

2. **对于 Claude Code 用户**：
   - 可选 **SuperPowers**（官方 marketplace 支持）
   - 或选 **OpenSpec**（需求管理）

3. **对于团队项目**：
   - 推荐 **OpenSpec**（规格持久化，支持协作）
   - 可叠加 **SuperPowers**（流程控制）

4. **避免过度组合**：
   - 三者功能有重叠，组合越多复杂度越高
   - 建议根据核心需求选择 1-2 个工具

---

## 参考链接

- OpenSpec: https://openspec.dev | https://github.com/Fission-AI/OpenSpec
- SuperPowers: https://github.com/obra/superpowers
- oh-my-openagent: https://ohmyopenagent.com | https://github.com/code-yeongyu/oh-my-openagent
- OpenCode: https://opencode.ai

---

*报告生成时间：2026-04-30*
