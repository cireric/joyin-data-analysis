# Markdown 转 Word 工具设计

## 目标

在 `scripts/md2word.py` 中实现一个 Markdown 文件转 Word 文档的 CLI 工具，针对合同文本场景优化。

## 方案选择

采用 **pypandoc**（Pandoc Python 封装），原因：
- 合同文本对格式保真度要求高
- Pandoc 对 Markdown→docx 转换最成熟
- 支持 `--reference-docx` 样式模板，适合合同品牌样式
- 纯 Python 库调用，开发成本低

## CLI 接口

```
python scripts/md2word.py input.md
python scripts/md2word.py input.md -o output.docx
python scripts/md2word.py input.md --reference-docx template.docx
python scripts/md2word.py input.md --toc --force
```

### 参数

| 参数 | 说明 |
|------|------|
| `input` | 输入 .md 文件（必填） |
| `-o / --output` | 输出 .docx 路径（默认同文件名） |
| `--reference-docx` | Pandoc 样式参考模板 |
| `--toc` | 生成目录 |
| `-f / --force` | 强制覆盖已存在文件 |
| `--debug` | 输出调试信息 |

## 架构

参照 `pdf2word.py` 模式：

```
Md2WordError
├── InputFileNotFoundError  — 文件不存在
├── InvalidMarkdownError    — 文件格式错误（非 .md）
├── ConversionError         — 转换过程错误
├── DependencyError         — Pandoc/pypandoc 未安装
```

### 函数

| 函数 | 职责 |
|------|------|
| `parse_args()` | 解析命令行参数 |
| `validate_input(path)` | 验证 .md 文件存在且扩展名正确 |
| `resolve_output(input_path, output_arg, force)` | 确定输出路径，--force 保护 |
| `convert_md_to_docx(input_path, output_path, reference_docx, toc, debug)` | 核心转换逻辑 |
| `main()` | 流程编排 |

## 依赖

`requirements.txt` 新增：
```
pypandoc==1.14
```

用户需额外安装 Pandoc 二进制。

## 错误处理

- 文件不存在 / 扩展名不对 → 明确提示并 exit(1)
- Pandoc/pypandoc 未安装 → 给出安装指引
- 转换失败 → 打印错误信息
- 输出文件已存在且未指定 --force → 阻止覆盖
