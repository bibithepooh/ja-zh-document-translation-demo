# AI-Assisted Japanese–Chinese Technical Document Translation Workflow

基于本人实际项目经验重新构建的中日技术文档翻译与质量校验工作流脱敏 Demo。

## 项目背景

在智能驾驶项目实习期间，团队需要频繁处理中日双语技术文档。由于日常项目任务较多，人工翻译通常只能利用零散时间完成，一份约 50 页的文件往往需要跨 3 个工作日交付。

为缩短处理周期、减少重复操作，我独立开发了技术文档翻译 Skill，并通过飞书自建应用和 Feishu MCP Server 接入团队协作入口。投入使用后，约 50 页技术文档的处理时间缩短至 30–60 分钟。

## 工具与分工

- **Claude Code**：协助生成和修改代码、定位报错。
- **Claude Sonnet 4.6**：用于领域分析、术语提取、初步翻译和图片文字识别。
- **我负责**：需求梳理、流程设计、文件处理程序开发与调试、翻译和格式规则制定、飞书接入、测试、验收及最终结果判断。

## 原工作流覆盖范围

- DOCX、PDF、PPTX、XLSX 与图片
- 技术领域识别、术语提取与中日双向翻译
- 数字、英文缩写和固定术语保护
- 原文加蓝色译文的翻译版，以及纯目标语言版输出
- 针对不同文件结构的格式保留
- 人工复核与异常项确认

## 公开 Demo 与原 Skill 的关系

本仓库是根据原项目规则重新实现的公开演示，不是原生产代码的直接复制。

- 原 Skill 使用 OpenAI 模型完成领域分析、动态术语提取和中日双向翻译，并覆盖 DOCX、PDF、PPTX、XLSX 与图片。
- 本 Demo 聚焦日文 XLSX 到中文的处理，优先读取仓库内的公开样例翻译缓存；遇到缓存外文本时使用公开翻译接口生成初稿，再执行固定术语校正。
- 两者采用相同的交付思路：生成“原文在前、蓝色译文在后”的翻译版，以及只保留目标语言的纯翻译版。

这样处理是为了让作品可以公开运行，同时不上传原公司的代码、术语表、接口配置和业务文档。

## 隐私与保密

本仓库不包含原公司或客户的源代码、文档、数据、项目名称、会议记录、接口配置、API Key、App Secret 或其他内部信息。Excel 样例来自日本国土交通省公开资料。作品 Demo 的在线初译模式仅面向公开样例，禁止上传公司或客户的非公开文件。

## 直接查看成果

不运行程序也可以直接下载下方两份 Excel，查看最终效果。

- [翻译版：日语原文 + 蓝色中文译文](outputs/excel-public-sample/自动驾驶安全标准审查表_翻译版.xlsx)
- [纯中文版](outputs/excel-public-sample/自动驾驶安全标准审查表_中文版.xlsx)

## 在 Windows 上运行 Demo

需要先安装 [Python 3.10 或更高版本](https://www.python.org/downloads/)，并在安装时勾选 `Add Python to PATH`。

1. 下载并解压本仓库。
2. 双击 `start_demo.bat`。
3. 第一次启动会自动创建本地运行环境并安装依赖，完成后浏览器会打开 `http://127.0.0.1:4173/`。
4. 上传仓库内的 `samples/mlit-autonomous-driving-xlsx/source-ja.xlsx` 进行测试。

首次安装依赖和处理缓存外文本时需要联网。程序不会把 API Key 写入仓库，也不需要 OpenAI API Key。

如需手动启动：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe server.py
```

## 输出规则

选择 XLSX 后会生成可下载的翻译版和纯中文版。翻译版遵循“日语原文在前，蓝色小字号中文译文另起一行附在后”的规则，并保留源表的合并单元格、填充、边框、行列尺寸与下拉框。

示例源文件及出处说明见 [`samples/mlit-autonomous-driving-xlsx/`](samples/mlit-autonomous-driving-xlsx/)。该译文仅用于演示工作流，不是日本国土交通省发布的官方中文版本。
