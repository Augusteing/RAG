# PHM知识图谱项目

本项目旨在从航空航天领域的 PHM（预测与健康管理）学术文献中自动抽取实体和关系，构建领域知识图谱，并提供评估与分析工具。

**重点特性**
- 基于 LangChain 的 RAG 检索增强抽取（BGE-large-zh-v1.5 Embeddings + Chroma）。
- 支持多模型提供方：DeepSeek、Gemini、Kimi（三套抽取脚本）。
- 仅保存干净结果 JSON（`entities`、`relations`），按阶段分目录：`test`、`priority_remain`、`others`。
- 支持不同实验的 Prompt 选择：`exp02` 使用新路径，`exp03` 支持逐论文 Prompt。

**环境要求**
- Python 3.10/3.11，建议使用 conda 管理环境。
- Windows 环境已验证（PowerShell / Anaconda Prompt）。

## 快速开始

- 创建 conda 环境：
  - `conda env create -f environment.yml`
  - `conda activate phm_knowledge`
- 设置 API Keys（复制 `.env.example` 为 `.env` 并填写）：
  - `DEEPSEEK_API_KEY`、`GEMINI_API_KEY`、`KIMI_API_KEY`
- 构建 RAG 向量数据库（LangChain 版）：
  - `python src/rag/build_pattern_vectorstore_langchain.py`
- 运行抽取（示例）：
  - DeepSeek：`python src/extraction/extractors/exact_deepseek_rag.py --exp exp02`
  - Gemini：`python src/extraction/extractors/exact_gemini_rag.py --exp exp02`
  - Kimi：`python src/extraction/extractors/exact_kimi_rag.py --exp exp02`

## 目录与文件说明（真实项）

**根目录**
- `.env.example`：环境变量模板（API Keys 等）。
- `environment.yml`：conda 环境定义（推荐用此创建环境）。
- `requirements.txt`：pip 依赖列表（备选安装方式）。
- `README.md`：项目说明（本文件）。
- `README_NEW.md`：另一版说明文档（草稿/补充）。
- `PROJECT_STRUCTURE.md`、`QUICK_START.md`：项目结构与快速开始补充文档。
- `Rag_code.rar`：历史/归档的代码压缩包。

**configs/**
- `schemas/phm_semantic_patterns.json`：领域 Schema，定义实体类型与关系类型，抽取脚本和评估使用此结构。
- `prompts/exp02/prompt.txt`：实验二（exp02）默认 Prompt（抽取脚本在 `exp02` 下读取此路径）。
- `prompts/exp03/`：实验三（exp03）逐论文 Prompt 目录，按论文文件名匹配。
- `prompts/prompt_eva.txt`：评估场景的 Prompt（如需）。
- `models/bge-large-zh-v1.5/`：本地化 Embeddings 模型目录（如使用本地模型）。
- `model_configs/README.md`：模型配置说明。

**data/**
- `raw/papers/`：待抽取的论文 Markdown 文件（分为 `test/`、`priority_remaining/`、`others/`）。
- `vectorstores/langchain_chroma_db/`：RAG 向量数据库（LangChain/Chroma 持久化目录）。
- `vectordb/chroma_db/`：另一套向量库目录（历史/备用）。
- `prompts/*_rag_examples/`：各模型的示例 Prompt 存放目录（当前脚本已不再写入示例）。
- `processed/`：处理后的中间数据与依赖模式（分析/构建向量库可用）。
- `results/deepseek_rag/`：历史抽取结果目录（现统一使用 `outputs/extractions/...`）。

**outputs/**
- `extractions/exp02/`、`extractions/exp03/`：抽取输出根目录（按实验分流）。
  - `deepseek_rag/`、`gemini_rag/`、`kimi_rag/`：按提供方分目录。
  - 阶段子目录：`test/`、`priority_remain/`、`others/`，每篇论文一个 JSON 文件，仅包含 `entities` 与 `relations`。
- `logs/exp02/`、`logs/exp03/`：运行日志（抽取汇总、耗时统计等），`exo03/` 为历史/拼写残留目录。
- `analysis/`：分析输出（一致性、评估结果、抽取时间统计等）。
- `evaluations/exp02/`、`evaluations/exp03/`：评估相关输出与导入任务（例如人工标注的任务 JSON）。
- `knowledge_graph/`：知识图谱相关产物说明（README）。

**src/**
- `extraction/extractors/`：三套抽取脚本（RAG 增强版）：
  - `exact_deepseek_rag.py`：DeepSeek 抽取；仅保存结果 JSON；按阶段分目录输出；支持 `--exp exp02|exp03`；读取 `configs/prompts/exp02/prompt.txt` 或逐论文 Prompt。
  - `exact_gemini_rag.py`：Gemini 抽取；同上行为；通过 OpenAI 兼容端点调用。
  - `exact_kimi_rag.py`：Kimi 抽取；同上行为；Moonshot/Kimi 兼容端点。
- `rag/`：向量库构建与工具：
  - `build_pattern_vectorstore_langchain.py`：基于 LangChain 的向量库构建（推荐）。
  - `build_pattern_vectorstore.py`：另一实现（可选）。
- `analysis/`：对抽取结果的分析脚本：一致性、评估结果、抽取时间统计等。
- `evaluation/`：评估脚本：`evaluate_extractions.py`（对抽取 JSON 进行评估）。
- `tools/`：辅助工具（下载模型、测试本地 Embeddings 等）。
- `utils/`：通用工具。

**tests/**
- `test_bge_embedding.py`：Embedding 测试。
- `demo_rag_enhancement.py`：RAG 增强 demo。
- `env_diagnostic.py`：环境诊断脚本。
- `README.md`、`__init__.py`：测试套件说明与初始化。

**docs/**
- 项目说明、结构对比、工作总结等文档（Markdown/PDF）。

**metadata/**
- 数据统计与校验脚本（元数据补充、规则验证等）。

## 运行约定与环境变量

- 抽取脚本需要对应 API Key：
  - `DEEPSEEK_API_KEY`、`GEMINI_API_KEY`、`KIMI_API_KEY`
- RAG 相关环境变量：
  - `RAG_ENABLED=1`（启用）／`0`（禁用）、`RAG_TOP_K=5`。
  - 可设置 `BGE_LOCAL_PATH`、`EMBEDDING_DEVICE=cuda|cpu`（如需要本地化 Embeddings）。
- 实验选择：
  - 命令行 `--exp exp02|exp03` 优先，其次读取 `EXP_ID` 环境变量，默认 `exp02`。

## 人工标注（可选）

- 推荐使用 Label Studio 进行 `test` 的 20 篇人工标注，支持实体与关系；导出 JSON 后可转换为本项目使用的干净格式（仅 `entities`、`relations`）。
- 导入任务可从 `data/raw/papers/test` 生成，导出结果建议放置到 `outputs/evaluations/{EXP_ID}/` 或直接对齐到 `outputs/extractions/{EXP_ID}/{provider}/test/` 结构用于评估与对比。

## 贡献与许可

- 欢迎提交 Issue 和 PR。
- 许可：MIT License。
