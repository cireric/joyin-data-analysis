# URL to Markdown 抓取工具设计文档

**日期：** 2026-05-07  
**状态：** 设计确认

---

## 概述

创建一个命令行工具，使用 Playwright 抓取网页内容并转换为 Markdown 格式保存到本地。支持单篇文章页和列表页（自动检测），具备风控规避机制。

---

## 功能需求

### 核心功能

1. **单篇文章抓取** - 输入文章 URL，抓取并保存为 Markdown
2. **列表页抓取** - 输入列表页 URL，自动提取所有文章链接并逐一抓取
3. **自动检测** - 根据URL和页面内容自动判断是文章页还是列表页
4. **图片处理** - 支持保留远程链接或下载到本地

### 支持平台

| 平台 | 文章页 | 列表页 | 特殊处理 |
|------|--------|--------|---------|
| 微信公众号 | ✅ | ✅ | 历史消息需滚动加载 |
| 知乎专栏 | ✅ | ✅ | 需处理登录墙 |
| 简书 | ✅ | ✅ | - |
| 通用网页 | ✅ | ❌ | 尝试提取 article/main |

---

## 命令行接口

### 使用示例

```bash
# 单篇文章
python scripts/url2md.py "https://mp.weixin.qq.com/s/xxx"

# 列表页
python scripts/url2md.py "https://mp.weixin.qq.com/mp/profile_ext?action=home&..."

# 指定输出目录
python scripts/url2md.py <url> --output misc/my-articles/

# 下载图片到本地
python scripts/url2md.py <url> --download-images

# 指定图片保存目录
python scripts/url2md.py <url> --download-images --images-dir misc/images/

# 控制抓取频率
python scripts/url2md.py <url> --delay 3 --max-delay 10

# 限制数量
python scripts/url2md.py <url> --limit 20

# 断点续传
python scripts/url2md.py <url> --resume state.json
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 文章页或列表页 URL | 必填 |
| `--output` | 输出目录 | `misc/` |
| `--filename` | 文件名（仅单篇有效） | 从标题生成 |
| `--download-images` | 下载图片到本地 | 否（保留远程链接） |
| `--images-dir` | 图片保存目录 | `<output>/images/` |
| `--limit` | 列表页最大抓取数 | 无限制 |
| `--delay` | 基础延迟（秒） | 2 |
| `--max-delay` | 最大延迟（秒） | 5 |
| `--randomize` | 随机延迟 | 启用 |
| `--cookies` | 加载 cookies 文件 | 无 |
| `--save-cookies` | 保存 cookies 到文件 | 无 |
| `--resume` | 从状态文件恢复 | 无 |
| `--state` | 保存状态文件路径 | `url2md-state.json` |

---

## 技术设计

### 文件结构

```
src/
  data_analysis/      # 数据分析模块（现有）
    loader.py
    analyzer.py
    ...
  
  data_crawl/         # 网页抓取模块（新建）
    __init__.py
    extractor.py      # 提取器核心逻辑
    selectors.py      # 各平台选择器配置
    downloader.py     # 图片下载器
    browser.py        # 浏览器配置与风控规避
    utils.py          # 工具函数（延迟、重试等）

scripts/
  url2md.py           # CLI 入口
```

### 模块职责

#### `scripts/url2md.py`
- 解析命令行参数
- 调用 `data_crawl` 模块执行抓取
- 显示进度和结果

#### `src/data_crawl/extractor.py`
- 页面类型检测（文章页/列表页）
- 文章内容提取
- 列表链接提取
- Markdown 转换

#### `src/data_crawl/selectors.py`
- 各平台的 CSS 选择器配置
- URL 匹配规则
- 平台特定处理逻辑

#### `src/data_crawl/downloader.py`
- 图片下载
- 文件命名
- 去重处理

#### `src/data_crawl/browser.py`
- Playwright 浏览器配置
- 浏览器指纹伪装
- 会话管理（cookies）

#### `src/data_crawl/utils.py`
- 随机延迟
- 指数退避重试
- 状态文件读写
- 文件名清理

---

## 风控规避机制

### 1. 请求频率控制

- **随机延迟**：每次请求间隔 `delay ± random(0, 1)` 秒
- **指数退避**：遇到 429/503 错误时，等待时间翻倍（1s → 2s → 4s → 8s，最大 60s）
- **默认延迟**：2 秒，最大 5 秒

### 2. 浏览器指纹伪装

```python
browser = await playwright.chromium.launch(
    headless=True,
    args=[
        '--disable-blink-features=AutomationControlled',
    ]
)

context = await browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    viewport={'width': 1920, 'height': 1080},
    locale='zh-CN',
    timezone_id='Asia/Shanghai',
)
```

### 3. 模拟人类行为

- **随机滚动**：列表页滚动距离随机（300-800px）
- **滚动暂停**：滚动后等待 0.5-1.5 秒
- **页面等待**：等待关键元素出现，而非固定时间

### 4. 会话复用

- 列表页和文章页使用同一个浏览器上下文
- 支持加载/保存 cookies
- 保持登录状态

### 5. 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 429 Too Many Requests | 等待 60 秒后重试，最多 3 次 |
| 503 Service Unavailable | 指数退避重试 |
| 连接超时 | 等待 5 秒重试 |
| 页面加载失败 | 跳过当前文章，记录错误日志 |
| 验证码/登录墙 | 停止抓取，提示用户手动处理 |

### 6. 断点续传

- 保存已抓取 URL 列表到状态文件
- 重新运行时跳过已完成的 URL
- 支持从指定位置继续

**状态文件格式：**
```json
{
  "url": "https://...",
  "total": 50,
  "completed": ["url1", "url2"],
  "failed": ["url3"],
  "last_update": "2024-01-01 12:00:00"
}
```

---

## 进度显示

### 列表页抓取

```
[INFO] 检测到列表页，正在提取文章链接...
[INFO] 发现 25 篇文章

抓取进度: [████████░░░░░░░░░░░░] 10/25 (40%) | 当前: 沙丘究竟有什么好看的
预计剩余: 30 秒 | 成功: 10 | 失败: 0

[INFO] 完成! 保存到: misc/
[INFO] 总计: 25 篇 | 成功: 25 | 失败: 0 | 耗时: 2分15秒
```

### 单篇文章

```
[INFO] 检测到文章页
[INFO] 正在抓取: 沙丘究竟有什么好看的
[INFO] 完成! 保存到: misc/沙丘究竟有什么好看的.md
```

---

## 图片处理

### 默认（保留远程链接）

```markdown
![图片](https://mmbiz.qpic.cn/mmbiz_jpg/xxx/640?wx_fmt=jpeg)
```

### 启用 `--download-images`

```markdown
![图片](images/沙丘究竟有什么好看的/img_001.jpeg)
```

### 图片保存结构

```
<output>/
  沙丘究竟有什么好看的.md
  images/
    沙丘究竟有什么好看的/
      img_001.jpeg
      img_002.png
      ...
```

---

## Markdown 输出格式

```markdown
# 文章标题

**作者：** xxx  
**发布时间：** 2024-01-01  
**来源：** https://mp.weixin.qq.com/s/xxx

---

正文内容...

![图片](images/xxx/img_001.jpeg)

更多内容...
```

---

## 依赖

### 新增依赖

```
playwright>=1.40.0
```

### 安装

**重要：所有操作必须在虚拟环境中进行**

```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Unix

# 安装依赖
pip install playwright

# 安装浏览器
playwright install chromium
```

### 运行与测试

所有命令均在虚拟环境中执行：

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 运行脚本
python scripts/url2md.py <url>

# 运行测试
python -m pytest tests/test_url2md.py -v
```

---

## 成功标准

1. 单篇文章抓取成功，Markdown 格式正确
2. 列表页自动识别并批量抓取
3. 进度显示清晰准确
4. 风控机制有效（无频繁封禁）
5. 断点续传功能正常
6. 图片下载功能正常
7. 支持 3+ 平台（微信、知乎、简书）
