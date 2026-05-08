# PDF转Word格式优化设计

## 概述

优化现有pdf2word脚本，提升合同PDF转换的格式还原度，解决字体样式丢失和段落格式错乱问题。

## 问题分析

当前转换合同PDF时存在以下问题：
- 字体样式丢失（字体、字号、粗体/斜体）
- 合同开头甲方、乙方展示格式与原文差异较大

## 目标

- 提升格式还原度，尽量接近"无损"转换
- 保持工具简单易用的CLI接口
- 支持调试模式帮助定位格式问题

## 技术方案

### pdf2docx参数优化

通过调整pdf2docx的转换参数提升格式还原：

| 参数 | 默认值 | 优化值 | 说明 |
|------|--------|--------|------|
| recover_tables | False | True | 增强表格恢复 |
| min_vertical_gap_width | 2.0 | 1.0 | 减小段落间距识别阈值 |
| multi_processing | False | True | 多进程加速大文件处理 |

### 转换模式

提供两种转换模式：

1. **normal模式**（默认）- 平衡速度与质量
2. **strict模式** - 更精确的格式还原，处理时间更长

### 调试功能

添加 `--debug` 参数：
- 输出详细转换日志
- 生成调试图片到临时目录

## CLI接口

```bash
# 基本转换（优化后）
python scripts/pdf2word.py contract.pdf

# 严格模式
python scripts/pdf2word.py contract.pdf --mode strict

# 调试模式
python scripts/pdf2word.py contract.pdf --debug

# 组合使用
python scripts/pdf2word.py contract.pdf --mode strict --debug
```

### 新增参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --mode | 转换模式：normal/strict | normal |
| --debug | 输出调试信息 | False |

## 文件改动

- `scripts/pdf2word.py` - 修改convert_pdf_to_docx函数，添加参数解析

## 成功标准

- 字体样式保留率提升
- 段落格式与原文更接近
- 调试模式能输出有用信息
