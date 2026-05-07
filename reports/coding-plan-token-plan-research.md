# 国内外模型厂家 Coding Plan 与 Token Plan 调研报告

> 调研日期：2026年5月
> 数据来源：官方文档、GitHub开源项目、实测数据

---

## 目录

1. [术语说明](#术语说明)
2. [核心选购建议](#核心选购建议)
3. [国内厂商 Coding Plan](#国内厂商-coding-plan)
4. [国外平台与服务](#国外平台与服务)
5. [按用量计费方案](#按用量计费方案)
6. [AI IDE/CLI Plan](#ai-idecli-plan)
7. [模型参数对比](#模型参数对比)
8. [总结与建议](#总结与建议)

---

## 术语说明

| 术语 | 说明 |
|------|------|
| **周期** | `5h` = 5小时 | `w` = 周 | `mo` = 月 |
| **额度倍率** | 当前周期额度 ÷ 包月价格（倍率越高，性价比越高） |
| **TPS** | Tokens Per Second，每秒生成Token数 |
| **RPM** | Requests Per Minute，每分钟请求数 |
| **上下文长度** | 模型支持的最大输入Token数 |

---

## 核心选购建议

### 🎁 免费方案

| 方案 | 特点 | 适用场景 |
|------|------|----------|
| **NVIDIA NIM** | deepseek-v4-pro/glm-5.1/minimax-m2.7 等开源模型免费，Up to 40 RPM | 评估测试、轻度使用 |
| **Ollama Free** | 本地运行开源模型，完全免费，隐私保护 | 本地开发、隐私敏感场景 |

### 💰 按用量计费首选

| 方案 | 特点 | 价格 |
|------|------|------|
| **DeepSeek V4 Flash** | 性价比最高，50+ TPS，1M上下文 | 输入¥1/百万Token，输出¥2/百万Token |
| **DeepSeek V4 Pro** | 旗舰模型，2.5折优惠至2026/05/31 | 输入¥3/百万Token，输出¥6/百万Token |

### 🏆 Coding Plan 推荐

| 需求 | 推荐方案 | 价格 | 理由 |
|------|----------|------|------|
| 个人开发者 | **MiniMax Coding Plan Plus** | ¥49/月 | 倍率最高(88.65)，含TTS和图像生成 |
| 团队协作 | **Kimi Code Allegretto** | ¥199/月 | 支持多模态，送专属龙虾，代码能力强 |
| 代码优先 | **GLM Coding Plan Pro** | ¥149/月 | 国内代码能力最强 |

---

## 国内厂商 Coding Plan

### 1. 智谱AI (GLM)

#### 官方信息
- **官网**: https://bigmodel.cn/glm-coding
- **模型**: GLM-5.1, GLM-4.7

#### 套餐详情

| 套餐 | 价格 | 额度说明 | TPS |
|------|------|----------|-----|
| Lite | ¥49/月 | 3x Claude Pro 用量，约80次/5h | 26.8 |
| Pro | ¥149/月 | 5x Lite 用量，约400次/5h | 26.8 |

#### 实测数据

| 指标 | Lite | Pro |
|------|------|-----|
| 5h 请求数 | 90 | 450 |
| 5h Tokens | 600万 | 3000万 |
| 月 Tokens | 1.28亿 | 6.4亿 |
| 额度倍率 | 5.08 | 8.35 |

#### 优缺点
- ✅ 国内代码能力最强
- ✅ 支持 Anthropic API 格式
- ❌ 不支持多模态（GLM-5.1 仅文本）
- ❌ 算力紧张，429 错误频繁

---

### 2. Moonshot AI (Kimi)

#### 官方信息
- **官网**: https://www.kimi.com/membership/pricing
- **模型**: kimi-k2.5, kimi-k2.6

#### 套餐详情

| 套餐 | 价格 | 额度说明 | TPS |
|------|------|----------|-----|
| Andante | ¥49/月 | Kimi Code 可调用 | 27.98 |
| Allegretto | ¥199/月 | 20倍额度 | 27.98 |

#### 实测数据

| 指标 | Andante | Allegretto |
|------|---------|------------|
| 5h 请求数 | 359 | 1307 |
| 5h Tokens | 1500万 | 6500万 |
| 月 Tokens | 8400万 | 14.28亿 |
| 额度倍率 | 2.48 | 9.89 |

#### 优缺点
- ✅ 支持多模态（图像输入）
- ✅ 代码能力强
- ✅ 送专属龙虾
- ❌ ¥49 套餐性价比低
- ❌ 最近算力紧张，TPS 下降

---

### 3. MiniMax

#### 官方信息
- **官网**: https://platform.minimaxi.com/subscribe/token-plan
- **模型**: minimax-m2.5, minimax-m2.7

#### 套餐详情

| 套餐 | 价格 | 额度说明 | TPS |
|------|------|----------|-----|
| Starter | ¥29/月 | 基础额度 | - |
| Plus | ¥49/月 | 1500次/5h | 52.6 |

#### 实测数据

| 指标 | Plus |
|------|------|
| 5h 请求数 | 1360 |
| 5h Tokens | 6000万 |
| 月 Tokens | 24亿 |
| 额度倍率 | **88.65** |

#### 优缺点
- ✅ **性价比最高**，倍率 88.65
- ✅ 包含 TTS 和图像生成
- ✅ TPS 稳定
- ❌ 不支持多模态（仅文本输入）

---

### 4. 阿里云百炼

#### 官方信息
- **官网**: https://www.aliyun.com/benefit/scene/codingplan
- **模型**: Qwen3.5-Plus, Qwen3-Max, Qwen3-Coder-Next, MiniMax M2.5, GLM-5, Kimi-k2.5

#### 套餐详情（Lite 基础套餐已下线）

| 套餐 | 价格 | 额度说明 |
|------|------|----------|
| Lite (已下线) | ¥40/月 | 1200次/5h, 9000次/周, 18000次/月 |

#### 支持的 AI 工具
- Qwen Code
- Qoder
- OpenClaw
- OpenCode
- Claude Code
- Codex
- Cline
- Cursor
- Kilo CLI

#### 优缺点
- ✅ 支持模型最多
- ✅ 生态工具丰富
- ❌ Lite 套餐已下线

---

### 5. 火山方舟 (字节跳动)

#### 官方信息
- **官网**: https://www.volcengine.com/activity/codingplan
- **模型**: doubao-seed-2.0-pro

#### 套餐详情

| 套餐 | 价格 | 额度说明 | TPS |
|------|------|----------|-----|
| Lite | ¥40/月 | 数倍于 Claude Pro | 86.6 |

#### 实测数据

| 指标 | Lite |
|------|------|
| 5h 请求数 | 148 |
| 5h Tokens | 1000万 |
| 月 Tokens | 3.2亿 |
| 额度倍率 | 15.18 |

#### 优缺点
- ✅ TPS 最高（86.6）
- ✅ 价格实惠
- ❌ 模型选择有限

---

### 6. 小米 MiMo

#### 官方信息
- **官网**: https://platform.xiaomimimo.com/#/token-plan
- **模型**: mimo-v2.5, mimo-v2.5-pro

#### 套餐详情

| 套餐 | 价格 | Credits | TPS |
|------|------|---------|-----|
| Pro | ¥329/月 | 7亿 Credits | 46.7 |

#### 特殊活动
- **100T 创造者激励计划**: 申请通过可免费领取一个月 Standard/Pro/Max Token Plan
- **官网**: https://100t.xiaomimimo.com/

#### 计费规则
- MiMo-V2.5-Pro 256k 上下文：消耗 1 Token = 2 Credits

---

## 国外平台与服务

### 1. OpenCode

#### 官方信息
- **官网**: https://opencode.ai
- **Go 套餐**: $10/月（首月 $5）

#### 套餐详情

| 周期 | 额度 |
|------|------|
| 5h | $12 |
| 周 | $30 |
| 月 | $60 |

#### 支持模型
- GLM-5.1, GLM-5
- Kimi K2.5
- MiMo-V2-Pro, MiMo-V2-Omni
- MiniMax M2.5, MiniMax M2.7

#### 优缺点
- ✅ 支持国产模型
- ✅ 额度倍率高（6倍）
- ✅ 兼容多种 AI 工具

---

### 2. OpenRouter

#### 官方信息
- **官网**: https://openrouter.ai

#### 免费模型

| 模型 | 限制 |
|------|------|
| hy3-preview | 50 reqs/day |
| minimax-m2.5 | 50 reqs/day |
| qwen3-coder | 50 reqs/day |

#### 特点
- ✅ 多模型聚合平台
- ✅ 部分模型限免
- ❌ 免费额度有限

---

### 3. Ollama

#### 官方信息
- **官网**: https://ollama.com/pricing

#### 套餐详情

| 套餐 | 价格 | 并发模型 | 说明 |
|------|------|----------|------|
| Free | $0 | 1 | 本地模型无限，云端轻度使用 |
| Pro | $20/月 | 3 | 50x Free 云端用量 |
| Max | $100/月 | 10 | 5x Pro 云端用量 |

#### 特点
- ✅ 本地运行完全免费
- ✅ 隐私保护（数据不离开本地）
- ✅ 40,000+ 社区集成
- ✅ 支持 CLI、API、桌面应用

#### 云端模型
- 支持模型列表: https://ollama.com/search?c=cloud

---

### 4. NVIDIA NIM

#### 官方信息
- **官网**: https://build.nvidia.com

#### 免费模型

| 模型 | 限制 |
|------|------|
| deepseek-v4-pro | Up to 40 RPM |
| deepseek-v4-flash | Up to 40 RPM |
| glm-5.1 | Up to 40 RPM |
| glm-4.7 | Up to 40 RPM |
| minimax-m2.7 | Up to 40 RPM |

#### 特点
- ✅ 完全免费
- ✅ 支持主流开源模型
- ❌ 无稳定性保证
- ❌ 首 Token 时间较高

---

### 5. Claude (Anthropic)

#### 官方信息
- **官网**: https://claude.ai/upgrade

#### 套餐详情

| 套餐 | 价格 | 模型 |
|------|------|------|
| Pro | $20/月 | claude-sonnet-4.6 |
| Max | $100/月 | claude-opus-4.7 |

#### 实测数据（Pro, claude-sonnet-4.6）

| 指标 | 数值 |
|------|------|
| 5h 请求数 | 298 |
| 5h Tokens | 529万 |
| 月 Tokens | 1.92亿 |
| 额度倍率 | 7.38 |

#### 特点
- ✅ 模型能力强
- ✅ 1M 上下文
- ❌ 中文 Tokenizer 压缩率低（152.86%）
- ❌ 价格较高

---

### 6. ChatGPT (OpenAI)

#### 官方信息
- **官网**: https://chatgpt.com/pricing

#### 套餐详情

| 套餐 | 价格 | Codex 额度 |
|------|------|------------|
| Plus | $20/月 | 45-225 Local Messages/5h |
| Pro | $200/月 | 双倍 Codex 配额（至2026/5/31） |

#### 实测数据（Plus, gpt-5.4）

| 指标 | 数值 |
|------|------|
| 5h 请求数 | 490 |
| 5h Tokens | 2000万 |
| 月 Tokens | 4.8亿 |
| 额度倍率 | 14.8 |

---

## 按用量计费方案

### DeepSeek API

#### 官方信息
- **官网**: https://platform.deepseek.com
- **文档**: https://api-docs.deepseek.com/zh-cn/quick_start/pricing

#### 模型价格

| 模型 | 上下文 | 输入价格 | 输出价格 | 缓存命中 |
|------|--------|----------|----------|----------|
| deepseek-v4-flash | 1M | ¥1/百万 | ¥2/百万 | ¥0.02/百万 |
| deepseek-v4-pro | 1M | ¥3/百万* | ¥6/百万* | ¥0.025/百万 |

> *deepseek-v4-pro 2.5折优惠至 2026/05/31 23:59，原价 ¥12/¥24

#### 特点
- ✅ **性价比最高**
- ✅ 1M 上下文
- ✅ 缓存读价格领先业界（1/100）
- ✅ 50+ TPS 稳定
- ❌ 不支持多模态

#### 费用估算
- 1亿 Token 约 ¥9（输入输出比 115:1）
- 同等用量下比大部分 Coding Plan 更便宜

---

## AI IDE/CLI Plan

### 综合对比

| 产品 | 价格 | 额度类型 | 月额度价值 | 倍率 |
|------|------|----------|------------|------|
| OpenCode Go | $10 | Quota | $60 | 6.0 |
| Trae Pro | $10 | Usage | $20+ | >2 |
| GitHub Copilot Pro | $10 | Usage | $10 | 1.0 |
| Zed Pro | $10 | Usage | $5 | 0.5 |
| Cursor Pro | $20 | Usage | >=$20 | >=1 |
| Windsurf Pro | $20 | Quota | - | - |
| Kiro Pro | $20 | Task | $40 | 2.0 |
| Augment Code INDIE | $20 | Usage | $25 | 1.25 |
| Kilo Pass Starter | $19 | Usage | ~$26.6 | 1.4 |
| Factory Droid Pro | $20 | Usage | ~$48 | 2.4 |

### 详细说明

#### Cursor Pro
- **价格**: $20/月
- **额度**: $20 API usage + 更多 Auto/Composer 2 额度
- **特点**: 按用量计费，超出部分另付

#### Windsurf Pro
- **价格**: $20/月（2周免费试用）
- **额度**: 8-101 messages/day (Premium Model)
- **特点**: 无限 SWE-1.5

#### GitHub Copilot Pro
- **价格**: $10/月
- **状态**: 暂时不可用
- **说明**: 2026年6月1日起迁移到按用量计费

#### Trae Pro
- **价格**: $10/月
- **额度**: $20 Basic + 随机 Bonus（有用户收到 $130）
- **特点**: 7天免费试用，无限自动补全

---

## 模型参数对比

### Tokenizer 效率（以 GPT-5.4 为 100% 基准）

| 模型 | 发布时间 | 参数量 | 上下文 | Token比例 | 多模态 |
|------|----------|--------|--------|-----------|--------|
| kimi-k2.5 | 2026-01-27 | 1T A32B | 256K | 87.99% | ✅ |
| kimi-k2.6 | 2026-04-20 | 1T A32B | 256K | 87.99% | ✅ |
| minimax-m2.7 | 2026-03-18 | 230B A10B | 200K | 89.23% | ❌ |
| hy3 | 2026-04-23 | 295B A21B | 256K | 92.22% | ❌ |
| gemini-3.1-pro | 2026-02-19 | ~3T | 1M | 92.73% | ✅ |
| deepseek-v4-flash | 2026-04-24 | 284B A13B | 1M | 95.30% | ❌ |
| deepseek-v4-pro | 2026-04-24 | 1.6T A49B | 1M | 95.30% | ❌ |
| glm-5.1 | 2026-04-08 | 744B A40B | 200K | 95.93% | ❌ |
| qwen-3.5-plus | 2026-02-16 | 397B A17B | 1M | 95.97% | ✅ |
| gpt-5.4 | 2026-03-05 | ~3T | 1.05M | 100.00% | ✅ |
| mimo-v2.5-pro | 2026-04-22 | 1T A42B | 1M | 101.18% | ✅ |
| claude-sonnet-4.6 | 2026-02-17 | ~1T | 1M | 152.86% | ✅ |
| claude-opus-4.7 | 2026-04-16 | ~5T | 1M | 166.75% | ✅ |

> 数值越低，中文分词压缩率越高，成本优势越明显

---

## 总结与建议

### 按使用场景推荐

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| **免费体验** | NVIDIA NIM | 支持主流开源模型，完全免费 |
| **本地开发** | Ollama Free | 隐私保护，无限使用 |
| **个人轻度** | MiniMax Plus (¥49) | 性价比最高，倍率88.65 |
| **个人重度** | DeepSeek V4 Flash 按量 | 比 Coding Plan 更便宜 |
| **团队协作** | Kimi Allegretto (¥199) | 多模态支持，代码能力强 |
| **代码优先** | GLM Pro (¥149) | 国内代码能力最强 |
| **多模型需求** | 阿里云百炼 | 支持模型最多 |
| **国际用户** | OpenCode Go ($10) | 支持国产模型，额度倍率高 |

### 关键结论

1. **按量计费往往更划算**: DeepSeek V4 Flash 的按量计费比大部分 Coding Plan 更便宜

2. **额度倍率是关键指标**: MiniMax Plus 以 88.65 的倍率遥遥领先

3. **注意算力稳定性**: GLM 和 Kimi 最近算力紧张，429 错误频繁

4. **中文场景优选国产模型**: Tokenizer 压缩率更高，成本更低

5. **隐私场景选本地**: Ollama 完全本地运行，数据不离开设备

---

## 参考链接

1. [Awesome Coding Plan - GitHub](https://github.com/mahonzhan/awesome-coding-plan)
2. [Coding Plan Benchmark](https://coding.15o.cc/)
3. [DeepSeek API 定价](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)
4. [阿里云百炼 Coding Plan](https://www.aliyun.com/benefit/scene/codingplan)
5. [Ollama 定价](https://ollama.com/pricing)
6. [NVIDIA NIM](https://build.nvidia.com)

---

*本报告基于公开信息整理，价格和额度可能随时变动，请以官方最新信息为准。*
