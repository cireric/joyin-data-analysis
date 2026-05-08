# PDF转Word脚本设计

## 概述

开发一个命令行工具，将文字型PDF文件转换为Word文档，保留完整格式。

## 目标用户

需要将PDF文档转换为可编辑Word格式的用户，PDF来源为Word/WPS等导出的文字型PDF。

## 功能需求

### 核心功能
- 将单个PDF文件转换为Word(.docx)格式
- 保留原文档格式（字体、颜色、对齐、表格、图片）
- 支持指定输出路径
- 支持指定页码范围

### 非功能需求
- 纯Python实现，无需外部工具
- 简单易用的CLI界面
- 清晰的错误提示

## 技术方案

### 依赖库
- `pdf2docx` - PDF转Word核心库

### 文件结构
```
scripts/
  pdf2word.py          # 主脚本，CLI入口
```

### CLI接口

```bash
# 基本用法
python scripts/pdf2word.py input.pdf

# 指定输出路径
python scripts/pdf2word.py input.pdf -o output.docx

# 指定页码范围
python scripts/pdf2word.py input.pdf --pages 1-5
python scripts/pdf2word.py input.pdf --pages 1,3,5-10
```

### 参数说明
| 参数 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| input | 输入PDF文件路径 | 是 | - |
| -o, --output | 输出Word文件路径 | 否 | 输入文件名.docx |
| --pages | 页码范围 | 否 | 全部页面 |

## 处理流程

1. 解析命令行参数
2. 验证输入文件存在且为PDF格式
3. 解析页码范围（如指定）
4. 调用pdf2docx进行转换
5. 输出结果路径

## 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 输入文件不存在 | 提示"文件不存在: {path}"并退出 |
| 输入文件非PDF | 提示"文件格式错误: 需要PDF文件"并退出 |
| 转换失败 | 提示具体错误信息并退出 |
| 页码范围无效 | 提示"页码范围无效: {range}"并退出 |

## 成功标准

- 能正确转换文字型PDF为Word格式
- 保留原文档的基本格式（标题、段落、表格、图片）
- 命令行界面清晰易用
- 错误提示友好明确
