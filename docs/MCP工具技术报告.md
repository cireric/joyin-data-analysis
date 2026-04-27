# MCP 工具技术报告

> **文档目的**：详细介绍当前 OpenCode 环境中可用的 4 个 MCP (Model Context Protocol) 工具，提供可操作的使用指南和实战示例。

---

## 目录

1. [Context7 MCP - 文档与代码查询](#1-context7-mcp---文档与代码查询)
2. [gh_grep MCP - GitHub 代码搜索](#2-gh_grep-mcp---github-代码搜索)
3. [Playwright MCP - 浏览器自动化](#3-playwright-mcp---浏览器自动化)
4. [Vision MCP - 图像与视频分析](#4-vision-mcp---图像与视频分析)
5. [综合应用场景](#5-综合应用场景)

---

## 1. Context7 MCP - 文档与代码查询

### 1.1 工具概述

| 属性 | 说明 |
|------|------|
| **用途** | 为 AI 助手提供最新、版本特定的库文档和代码示例 |
| **核心价值** | 消除幻觉 API 和过时代码示例 |
| **服务地址** | `https://mcp.context7.com/mcp` |
| **认证方式** | API Key（环境变量 `CONTEXT7_API_KEY`） |

### 1.2 可用工具

#### `context7_resolve-library-id`
解析库名称到 Context7 兼容的库 ID。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `libraryName` | string | 是 | 库名称（使用官方名称，如 "Next.js" 而非 "nextjs"） |
| `query` | string | 是 | 任务描述，用于排序结果 |

**返回示例：**
```json
{
  "results": [
    {
      "id": "/vercel/next.js",
      "title": "Next.js",
      "description": "The React Framework for Production",
      "codeSnippets": 150,
      "sourceReputation": "High",
      "benchmarkScore": 95
    }
  ]
}
```

#### `context7_query-docs`
查询指定库的文档和代码示例。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `libraryId` | string | 是 | Context7 兼容的库 ID（如 `/mongodb/docs`） |
| `query` | string | 是 | 具体问题或任务描述 |
| `researchMode` | boolean | 否 | 深度研究模式（需要 API Key） |
| `tokensNum` | number | 否 | 返回 token 数量（1000-50000，默认 5000） |

### 1.3 实战示例

#### 示例 1：查找 React useState 文档
```
步骤1: 解析库ID
使用 context7_resolve-library-id:
  libraryName: "React"
  query: "useState hook examples"

步骤2: 查询文档
使用 context7_query-docs:
  libraryId: "/facebook/react"
  query: "How to use useState with TypeScript?"
```

#### 示例 2：查找 Python pandas 数据处理方法
```
使用 context7_query-docs:
  libraryId: "/pandas-dev/pandas"
  query: "How to filter dataframe by multiple conditions?"
  tokensNum: 3000
```

### 1.4 使用技巧

1. **先解析 ID 再查询**：除非用户直接提供了 `/org/project` 格式的 ID
2. **精确查询**：查询语句要具体，如 "React useEffect cleanup function" 而非 "hooks"
3. **调整 token 数**：简单问题用 1000-3000 tokens，复杂文档用 5000+
4. **重试机制**：首次查询不满意可启用 `researchMode: true`

---

## 2. gh_grep MCP - GitHub 代码搜索

### 2.1 工具概述

| 属性 | 说明 |
|------|------|
| **用途** | 搜索 GitHub 上数百万公开仓库的实际代码 |
| **核心价值** | 查找真实世界的代码模式和用法示例 |
| **服务地址** | `https://mcp.grep.app` |
| **搜索类型** | 代码模式匹配（类似 grep） |

### 2.2 可用工具

#### `gh_grep_searchGitHub`
在 GitHub 仓库中搜索代码模式。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 代码模式（实际代码，非关键词） |
| `repo` | string | 否 | 限定仓库（如 "facebook/react"） |
| `path` | string | 否 | 限定文件路径（如 "src/components/*.tsx"） |
| `language` | array | 否 | 限定编程语言（如 ["TypeScript", "TSX"]） |
| `useRegexp` | boolean | 否 | 是否使用正则表达式 |
| `matchCase` | boolean | 否 | 是否区分大小写 |
| `matchWholeWords` | boolean | 否 | 是否全字匹配 |
| `numResults` | number | 否 | 返回结果数量（默认 8） |

### 2.3 实战示例

#### 示例 1：查找 React ErrorBoundary 实现
```
使用 gh_grep_searchGitHub:
  query: "class ErrorBoundary extends"
  language: ["TypeScript", "TSX"]
  numResults: 5
```

#### 示例 2：查找 Python Flask CORS 配置
```
使用 gh_grep_searchGitHub:
  query: "CORS\\("
  language: ["Python"]
  useRegexp: true
  repo: "pallets/flask"
```

#### 示例 3：多行模式搜索 useEffect cleanup
```
使用 gh_grep_searchGitHub:
  query: "(?s)useEffect\\(\\(\\) => {.*removeEventListener"
  useRegexp: true
  language: ["JavaScript", "TypeScript"]
```

### 2.4 搜索技巧

1. **搜索实际代码**：搜索 `useState(` 而非 "react tutorial"
2. **使用正则**：复杂模式用 `(?s)pattern` 跨行匹配
3. **限定范围**：用 `repo`、`path`、`language` 缩小搜索范围
4. **最多调用 3 次**：找不到就调整查询，不要无限重试

---

## 3. Playwright MCP - 浏览器自动化

### 3.1 工具概述

| 属性 | 说明 |
|------|------|
| **用途** | 提供浏览器自动化能力，基于可访问性树（非像素） |
| **核心价值** | 让 AI 能够像人一样操作网页 |
| **工作方式** | 可访问性快照 + 元素引用 |
| **支持浏览器** | Chromium, Firefox, WebKit |

### 3.2 核心工具

#### 导航与页面管理
| 工具 | 说明 |
|------|------|
| `playwright_browser_navigate` | 导航到指定 URL |
| `playwright_browser_navigate_back` | 后退 |
| `playwright_browser_reload` | 刷新页面 |
| `playwright_browser_tabs` | 标签页管理（新建/切换/关闭） |
| `playwright_browser_resize` | 调整浏览器窗口大小 |

#### 页面交互
| 工具 | 说明 |
|------|------|
| `playwright_browser_snapshot` | 获取页面可访问性快照（含元素 ref） |
| `playwright_browser_click` | 点击元素 |
| `playwright_browser_type` | 输入文本 |
| `playwright_browser_fill_form` | 批量填写表单 |
| `playwright_browser_hover` | 悬停元素 |
| `playwright_browser_drag` | 拖拽操作 |
| `playwright_browser_press_key` | 按键操作 |
| `playwright_browser_select_option` | 下拉选择 |

#### 高级功能
| 工具 | 说明 |
|------|------|
| `playwright_browser_evaluate` | 执行 JavaScript |
| `playwright_browser_run_code` | 运行 Playwright 脚本 |
| `playwright_browser_file_upload` | 文件上传 |
| `playwright_browser_handle_dialog` | 处理对话框 |
| `playwright_browser_take_screenshot` | 截图 |
| `playwright_browser_wait_for` | 等待元素/文本/时间 |
| `playwright_browser_console_messages` | 获取控制台消息 |
| `playwright_browser_network_requests` | 获取网络请求 |

### 3.3 标准工作流

```
1. 导航: playwright_browser_navigate { url: "https://example.com" }
2. 快照: playwright_browser_snapshot → 获取元素 ref
3. 交互: 使用 ref 进行 click/type/fill 等操作
4. 验证: 再次快照或截图确认结果
```

### 3.4 实战示例

#### 示例 1：自动填写表单
```
1. playwright_browser_navigate: url = "https://example.com/contact"

2. playwright_browser_snapshot: {}
   → 获取表单元素的 ref，如:
     - textbox "姓名" [ref=e1]
     - textbox "邮箱" [ref=e2]
     - button "提交" [ref=e3]

3. playwright_browser_fill_form:
   fields = [
     { name: "姓名", ref: "e1", type: "textbox", value: "张三" },
     { name: "邮箱", ref: "e2", type: "textbox", value: "zhangsan@example.com" }
   ]

4. playwright_browser_click:
   ref: "e3"
   element: "提交按钮"
```

#### 示例 2：网页截图与内容提取
```
1. playwright_browser_navigate: url = "https://news.ycombinator.com"

2. playwright_browser_take_screenshot:
   filename: "hackernews.png"
   fullPage: true

3. playwright_browser_snapshot:
   filename: "page_content.md"
```

#### 示例 3：执行自定义 Playwright 脚本
```
playwright_browser_run_code:
  code: """
  async (page) => {
    await page.getByRole('button', { name: 'Load More' }).click();
    await page.waitForSelector('.article');
    return await page.title();
  }
  """
```

### 3.5 配置选项

| 环境变量 | CLI 参数 | 说明 |
|----------|-----------|------|
| `PLAYWRIGHT_MCP_VIEWPORT_SIZE` | `--viewport-size` | 视口大小（如 "1280x720"） |
| `PLAYWRIGHT_MCP_HEADLESS` | `--headless` | 无头模式 |
| `PLAYWRIGHT_MCP_BROWSER` | `--browser` | 浏览器选择（chromium/firefox/webkit） |
| `PLAYWRIGHT_MCP_TIMEOUT_ACTION` | `--timeout-action` | 操作超时（默认 5000ms） |

---

## 4. Vision MCP - 图像与视频分析

### 4.1 工具概述

| 属性 | 说明 |
|------|------|
| **用途** | 为 AI 提供视觉能力，分析图像和视频内容 |
| **核心价值** | OCR、UI 转代码、错误诊断、图表理解 |
| **支持格式** | 图像: PNG/JPG/JPEG (≤5MB), 视频: MP4/MOV/M4V (≤8MB) |
| **底层模型** | Z.AI GLM-4.6V / OpenAI GPT-4V 等视觉语言模型 |

### 4.2 可用工具

#### 核心工具列表

| 工具 | 说明 | 典型场景 |
|------|------|----------|
| `vision_ui_to_artifact` | UI 截图转代码/提示/规范/描述 | 设计稿转代码 |
| `vision_extract_text_from_screenshot` | OCR 提取文本 | 文档扫描、代码识别 |
| `vision_diagnose_error_screenshot` | 分析错误截图并给出修复建议 | 调试错误弹窗 |
| `vision_understand_technical_diagram` | 理解技术图表（UML/ER/架构图） | 系统设计分析 |
| `vision_analyze_data_visualization` | 分析图表和仪表盘 | 数据趋势提取 |
| `vision_ui_diff_check` | 比较两张 UI 截图差异 | UI 回归测试 |
| `vision_image_analysis` | 通用图像分析 | 不适合上述分类的场景 |
| `vision_video_analysis` | 分析视频内容 | 视频内容理解 |

### 4.3 详细参数说明

#### `vision_ui_to_artifact`
```json
{
  "image": "/path/to/screenshot.png 或 URL",
  "output_format": "code | prompt | design_spec | description",
  "extra_prompt": "附加指令（可选）"
}
```

#### `vision_extract_text_from_screenshot`
```json
{
  "image": "/path/to/screenshot.png 或 URL"
}
```
返回 OCR 提取的所有可见文本。

#### `vision_diagnose_error_screenshot`
```json
{
  "image": "/path/to/error.png 或 URL"
}
```
返回结构化诊断结果和修复建议。

#### `vision_understand_technical_diagram`
```json
{
  "image": "/path/to/diagram.png",
  "diagram_type": "UML | ER | architecture | flowchart (可选)"
}
```

#### `vision_analyze_data_visualization`
```json
{
  "image": "/path/to/chart.png"
}
```
返回趋势、异常和业务洞察。

#### `vision_ui_diff_check`
```json
{
  "image_before": "/path/to/before.png",
  "image_after": "/path/to/after.png",
  "description": "上下文描述（可选）"
}
```

### 4.4 实战示例

#### 示例 1：UI 截图转 React 代码
```
使用 vision_ui_to_artifact:
  image: "D:/screenshots/login-page.png"
  output_format: "code"
  extra_prompt: "使用 React + Tailwind CSS，包含表单验证"
```

#### 示例 2：OCR 提取文档文字
```
使用 vision_extract_text_from_screenshot:
  image: "D:/docs/scanned-form.jpg"
```
返回：
```
姓名：张三
部门：技术部
入职日期：2024-01-15
...
```

#### 示例 3：诊断错误弹窗
```
使用 vision_diagnose_error_screenshot:
  image: "D:/screenshots/error-popup.png"
```
返回：
```json
{
  "error_type": "TypeError",
  "message": "Cannot read properties of undefined",
  "likely_cause": "API 响应数据格式变更",
  "suggested_fixes": [
    "添加空值检查：data && data.items",
    "使用可选链：data?.items"
  ]
}
```

#### 示例 4：分析数据图表
```
使用 vision_analyze_data_visualization:
  image: "D:/reports/sales-chart.png"
```
返回：
```
- 销售额在 Q3 同比增长 23%
- 异常点：11月销售额骤降 40%，可能与促销活动结束有关
- 趋势：移动端销售额占比持续上升
```

#### 示例 5：UI 差异对比
```
使用 vision_ui_diff_check:
  image_before: "D:/screenshots/v1.png"
  image_after: "D:/screenshots/v2.png"
  description: "新版调整了导航栏颜色和按钮位置"
```

### 4.5 使用技巧

1. **本地路径优先**：将图片保存到本地目录，然后指定路径
2. **明确输出格式**：使用 `output_format` 指定需要的结果类型
3. **提供上下文**：使用 `extra_prompt` 或 `description` 补充背景信息
4. **文件大小限制**：图像 ≤5MB，视频 ≤8MB

---

## 5. 综合应用场景

### 5.1 场景 1：从设计到代码完整流程

```
1. 使用 vision_ui_to_artifact 将 UI 设计稿转为 React 代码
2. 使用 context7_query-docs 查询相关组件文档（如 "Material-UI Button API"）
3. 使用 gh_grep_searchGitHub 查找类似实现代码
4. 使用 playwright_browser_navigate 打开本地开发服务器
5. 使用 playwright_browser_snapshot + playwright_browser_screenshot 验证实现效果
```

### 5.2 场景 2：错误诊断与修复

```
1. 使用 vision_diagnose_error_screenshot 分析错误截图
2. 使用 context7_query-docs 查询相关 API 正确用法
3. 使用 gh_grep_searchGitHub 查看其他人如何解决类似问题
4. 修复代码后，使用 playwright 自动化测试验证
```

### 5.3 场景 3：数据分析报告生成

```
1. 使用 vision_analyze_data_visualization 分析图表趋势
2. 使用 vision_extract_text_from_screenshot 提取报表数据
3. 使用 context7_query-docs 查询 pandas/numpy 数据处理方法
4. 生成分析报告（当前项目的核心功能）
```

### 5.4 场景 4：竞品分析与学习

```
1. 使用 playwright_browser_navigate 访问竞品网站
2. 使用 playwright_browser_take_screenshot 截图关键页面
3. 使用 vision_ui_to_artifact 分析 UI 实现方式
4. 使用 gh_grep_searchGitHub 查找类似交互的实现代码
```

---

## 附录：工具快速参考

### Context7 快速参考
```
解析库ID: context7_resolve-library-id(libraryName, query)
查询文档: context7_query-docs(libraryId, query, tokensNum?)
```

### gh_grep 快速参考
```
代码搜索: gh_grep_searchGitHub(query, repo?, language?, useRegexp?)
```

### Playwright 快速参考
```
导航: playwright_browser_navigate(url)
快照: playwright_browser_snapshot()
点击: playwright_browser_click(ref, element)
输入: playwright_browser_type(ref, text)
截图: playwright_browser_take_screenshot(filename, fullPage?)
等待: playwright_browser_wait_for(text?, time?)
```

### Vision 快速参考
```
UI转代码: vision_ui_to_artifact(image, output_format)
OCR提取: vision_extract_text_from_screenshot(image)
错误诊断: vision_diagnose_error_screenshot(image)
图表分析: vision_analyze_data_visualization(image)
UI对比: vision_ui_diff_check(image_before, image_after)
通用分析: vision_image_analysis(image, prompt?)
```

---

## 总结

| MCP 工具 | 核心能力 | 最佳实践 |
|----------|----------|----------|
| **Context7** | 获取最新文档 | 先解析 ID，查询要具体 |
| **gh_grep** | 搜索真实代码 | 搜索代码模式，限定范围 |
| **Playwright** | 浏览器自动化 | 快照获取 ref，再交互 |
| **Vision** | 视觉分析 | 本地路径，明确输出格式 |

---

*文档生成时间：2026-04-27*
*维护者：OpenCode AI Agent*
