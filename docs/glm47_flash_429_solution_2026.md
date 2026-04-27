# 智谱 GLM-4.7-Flash 429 错误（业务码 1305）解决方案技术报告
> 生成时间：2026 年 4 月 26 日  
> 适用场景：OpenCode + OMO（Oh My OpenCode）用户，智谱 GLM-4.7-Flash 免费模型限流问题  
> 错误描述：`openai.RateLimitError: Error code: 429 - {'error': {'code': '1305', 'message': '该模型当前访问量过大，请您稍后再试'}}`

---

## 一、错误深度分析
### 1.1 错误码含义
| 错误类型 | 代码 | 含义 | 触发原因 |
|----------|------|------|----------|
| HTTP 429 | 429 | Too Many Requests（请求频率超限） | 触发智谱速率限制 |
| 业务码 1305 | 1305 | 该模型当前访问量过大，请您稍后再试 | 免费层达到 QPS/并发上限 |

### 1.2 速率限制详情（智谱免费层）
| 限制维度 | 阈值 | 说明 |
|----------|------|------|
| 每秒请求数（QPS） | 1 QPS | 单账号每秒最多 1 次请求 |
| 并发数 | 30 并发 | 同时处理的最大请求数 |
| 每分钟请求数（RPM） | ~60 RPM | 基于 QPS 换算 |

### 1.3 非服务器宕机确认
- 智谱官方无服务中断公告（`docs.bigmodel.cn` 仍标注免费调用）
- OpenRouter 监控显示 GLM-4.7-Flash 持续有调用量（近期 Prompt 1.56B tokens）
- 技术社区未出现"服务器负载过高导致完全不可用"的集中投诉
- GitHub 上 OpenCode 相关 Issue（如 [#2898](https://github.com/anomalyco/opencode/issues/2898)、[#11127](https://github.com/anomalyco/opencode/issues/11127)）均指向速率限制，非服务故障

---

## 二、立即生效方案（无需改配置）
### 2.1 等待重试（最快）
- 速率限制按**分钟**滚动计数，等待 **1-5 分钟** 后重试即可恢复
- OpenCode 内发送空消息触发重试：
  ```bash
  .  # 发送空消息，触发自动重试
  ```

### 2.2 降低请求频率
```python
# 简易速率控制中间件
import time

class RateLimiter:
    def __init__(self, qps=1):
        self.interval = 1.0 / qps
        self.last_request = 0
    
    def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_request = time.time()

limiter = RateLimiter(qps=1)
limiter.wait()  # 调用前等待
```

### 2.3 手动切换备用模型
```bash
# OpenCode 内临时切换
/model openrouter/z-ai/glm-4.5-air:free  # 用 OpenRouter 免费模型
/model ollama/glm-4.7-flash  # 切换本地模型
```

---

## 三、OMO 专属配置调整（永久生效）
配置文件路径：
- 全局：`~/.config/opencode/oh-my-opencode.jsonc`
- 项目：`.opencode/oh-my-opencode.jsonc`

### 3.1 开启自动降级（关键！默认关闭）
```jsonc
// oh-my-opencode.jsonc
{
  "runtime_fallback": {
    "enabled": true,
    "retry_on_errors": [429, 1305, 500, 503],
    "max_fallback_attempts": 3,
    "timeout_seconds": 30,
    "notify_on_fallback": true
  }
}
```
> 参考 [OMO Issue #2677](https://github.com/code-yeongyu/oh-my-openagent/issues/2677)：该功能默认禁用，需手动开启才会自动切换备用模型。

### 3.2 配置多模型降级链（per-agent）
```jsonc
{
  "agents": {
    "main": {
      "models": [
        { "model": "zai/glm-4.7-flash", "priority": 1 },
        { "model": "openrouter/z-ai/glm-4.5-air:free", "priority": 2 },
        { "model": "google/gemini-3-flash", "priority": 3 }
      ],
      "fallback_strategy": "sequential",
      "fallback_on": ["rate_limit", "error"]
    }
  }
}
```
> 参考 [OMO Issue #326](https://github.com/code-yeongyu/oh-my-openagent/issues/326)：支持为每个智能体配置多模型优先级链。

### 3.3 限制并发（避免触发 1305）
```jsonc
{
  "background_task": {
    "defaultConcurrency": 2,  // 全局最大并发
    "providerConcurrency": {
      "zai": 1,          // 智谱接口并发限制为1
      "zhipu": 1
    },
    "modelConcurrency": {
      "zai/glm-4.7-flash": 1
    }
  }
}
```
> 参考 [OMO 文档](https://github.com/code-yeongyu/oh-my-openagent/blob/master/docs/configurations.md)：控制 provider/model 级并发，避免频率超限。

### 3.4 增加超时与 Provider 配置
```jsonc
// opencode.json（主配置）
{
  "provider": {
    "zai": {
      "baseUrl": "https://open.bigmodel.cn/api/paas/v4",  // 国内端点，勿用国际版
      "options": { "timeout": 600000 }  // 10分钟超时
    },
    "zhipu": {
      "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
      "apiKey": "${ZHIPU_API_KEY}"
    }
  }
}
```
> 参考 [OpenCode Issue #2898](https://github.com/anomalyco/opencode/issues/2898)：智谱接口需增加超时；[Issue #12671](https://github.com/anomalyco/opencode/issues/12671)：区分 `zai` 和 `zhipu` provider。

---

## 四、长期架构方案
### 4.1 本地部署（彻底免限流）
#### Ollama 量化部署（仅需 12GB 显存）
```bash
# 1. 拉取量化模型
ollama pull glm4.7-flash:q4_K_XL

# 2. 启动服务（匹配 OpenCode 别名）
ollama serve --alias glm-4.7-flash --ctx-size 32768 --port 8080
```

#### OMO 配置本地模型
```jsonc
// oh-my-opencode.jsonc
{
  "agents": {
    "main": {
      "model": "ollama/glm-4.7-flash"  // 指向本地 Ollama
    }
  }
}
```
> 参考 [Running GLM-4.7-Flash Locally with OpenCode](https://www.pondhouse-data.com/blog/glm-4-7-flash-local-opencode)

### 4.2 API 聚合层（多 Provider 负载均衡）
```python
# 简易聚合器示例
class APIAggregator:
    def __init__(self):
        self.providers = {
            "zai": {"key": "YOUR_ZHIPU_KEY", "rpm": 1},
            "openrouter": {"key": "YOUR_OR_KEY", "rpm": 50},
            "local": {"type": "ollama", "rpm": 100}
        }
    
    def query(self, prompt):
        for provider in self.providers:
            try:
                return self._call_provider(provider, prompt)
            except RateLimitError:
                continue
        raise Exception("All providers rate limited")
```

---

## 五、监控与验证
### 5.1 关键命令
```bash
# 检查 OMO 状态
opencode doctor --verbose

# 查看当前配置
cat ~/.config/opencode/oh-my-opencode.jsonc

# 查看 OpenCode 模型状态
opencode models
```

### 5.2 日志查看
- OpenCode 日志：`~/.local/share/opencode/logs/`
- OMO 日志：关注 `runtime_fallback` 触发记录、`1305` 错误出现频率

---

## 六、总结与建议
### 6.1 核心结论
- 错误 `1305` 是**速率限制**，非服务器故障，等待 1-5 分钟可恢复
- OMO 的 `runtime_fallback` 默认关闭，是多数用户未触发自动降级的主因
- 智谱免费层限制严格（1 QPS），多智能体并发极易触发限流

### 6.2 推荐组合方案
1. **立即**：开启 OMO `runtime_fallback` + 限制智谱并发为 1
2. **短期**：配置多模型降级链（智谱 → OpenRouter 免费 → 本地模型）
3. **长期**：部署本地 GLM-4.7-Flash（Ollama 量化版），彻底避免限流

### 6.3 避坑指南
| 问题 | 解决方案 |
|------|----------|
| 配置不生效 | 检查是否存在项目级 `opencode.json` 覆盖全局配置 |
| 仍触发 1305 | 确认使用国内端点 `open.bigmodel.cn`，非国际版 `api.z.ai` |
| OMO 不降级 | 确保 `runtime_fallback.enabled: true` 且 `retry_on_errors` 包含 1305 |
| 本地模型慢 | 使用 `q4_K_XL` 量化版，显存≥12GB |

---
> 报告数据来源：智谱官方文档、OpenCode GitHub Issues、OpenRouter 监控数据、技术社区反馈（截至 2026 年 4 月 26 日）
