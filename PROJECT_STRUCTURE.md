# PHM知识图谱抽取项目 - 文件夹结构规范

## 📁 当前项目结构（已优化）

```
langchain/                              # 项目根目录
│
├── README.md                           # ⭐ 项目说明（待创建）
├── requirements.txt                    # ⭐ Python依赖（待创建）
├── environment.yml                     # ⭐ Conda环境配置（待创建）
├── .gitignore                          # ⭐ Git配置（待创建）
│
├── data/                               # 📊 数据目录（重组）
│   ├── raw/                            # 原始数据
│   │   ├── papers/                     # 📄 原始论文文献（从"论文文献"迁移）
│   │   │   ├── priority/               # 优先评估的论文
│   │   │   └── general/                # 通用论文
│   │   └── dependency_analysis/        # 依存句法分析结果（从"依存路径提取结果"迁移）
│   │       └── semantic_syntactic_patterns_report_2025-10-14_172830.csv
│   │
│   ├── processed/                      # 处理后的数据
│   │   ├── embeddings/                 # 向量数据库
│   │   │   └── chroma_db/              # ChromaDB持久化目录
│   │   └── extracted_kg/               # 抽取的知识图谱数据
│   │       ├── deepseek/               # DeepSeek模型结果
│   │       ├── gemini/                 # Gemini模型结果
│   │       └── kimi/                   # Kimi模型结果
│   │
│   └── interim/                        # 中间数据
│       └── validation/                 # 验证数据
│
├── configs/                            # ⚙️ 配置文件目录（重组）
│   ├── prompts/                        # Prompt模板
│   │   └── extraction_prompt.txt       # 从"prompt/prompt.txt"迁移
│   ├── schemas/                        # Schema定义
│   │   └── phm_semantic_patterns.json  # 从"schema文件"迁移
│   └── model_configs/                  # 模型配置
│       ├── deepseek_config.yaml
│       ├── gemini_config.yaml
│       └── kimi_config.yaml
│
├── src/                                # 💻 源代码目录（重组）
│   ├── __init__.py
│   │
│   ├── extraction/                     # 实体关系抽取模块
│   │   ├── __init__.py
│   │   ├── extractors/                 # 各模型抽取器
│   │   │   ├── __init__.py
│   │   │   ├── base_extractor.py       # 基础抽取器类
│   │   │   ├── deepseek_extractor.py   # 从"code/抽取/exact_deepseek.py"重构
│   │   │   ├── gemini_extractor.py     # 从"code/抽取/exact_gemini.py"重构
│   │   │   └── kimi_extractor.py       # 从"code/抽取/exact_kimi.py"重构
│   │   └── orchestrator.py             # 从"code/抽取/main.py"重构
│   │
│   ├── rag/                            # RAG检索增强模块（新增）
│   │   ├── __init__.py
│   │   ├── pattern_vectorizer.py       # 模式向量化
│   │   ├── pattern_retriever.py        # 模式检索器
│   │   └── prompt_enhancer.py          # Prompt增强器
│   │
│   ├── data_processing/                # 数据处理模块
│   │   ├── __init__.py
│   │   ├── metadata_filler.py          # 从"code/填充脚本"迁移
│   │   └── schema_validator.py         # Schema验证
│   │
│   ├── knowledge_graph/                # 知识图谱模块（新增）
│   │   ├── __init__.py
│   │   ├── graph_builder.py            # KG构建
│   │   ├── graph_query.py              # KG查询
│   │   └── graph_visualizer.py         # KG可视化
│   │
│   └── utils/                          # 工具模块
│       ├── __init__.py
│       ├── file_utils.py               # 文件操作
│       ├── logger.py                   # 日志工具
│       └── api_clients.py              # API客户端
│
├── scripts/                            # 🚀 可执行脚本
│   ├── 01_build_vector_db.py           # 构建向量数据库
│   ├── 02_run_extraction.py            # 运行抽取任务
│   ├── 03_merge_results.py             # 合并多模型结果
│   ├── 04_build_knowledge_graph.py     # 构建知识图谱
│   └── 05_query_kg.py                  # 查询知识图谱
│
├── notebooks/                          # 📓 Jupyter笔记本（新增）
│   ├── 00_data_exploration.ipynb       # 数据探索
│   ├── 01_pattern_analysis.ipynb       # 模式分析
│   ├── 02_extraction_evaluation.ipynb  # 抽取效果评估
│   └── 03_kg_visualization.ipynb       # 知识图谱可视化
│
├── outputs/                            # 📤 输出目录（重组）
│   ├── results/                        # 最终结果
│   │   ├── json/                       # JSON格式结果
│   │   ├── csv/                        # CSV格式结果
│   │   └── merged/                     # 合并后的结果
│   │
│   ├── logs/                           # 日志文件
│   │   ├── extraction/                 # 抽取日志
│   │   ├── rag/                        # RAG日志
│   │   └── errors/                     # 错误日志
│   │
│   ├── figures/                        # 图表（新增）
│   │   ├── kg_graphs/                  # 知识图谱可视化
│   │   └── statistics/                 # 统计图表
│   │
│   └── reports/                        # 报告（新增）
│       ├── extraction_summary.html
│       └── pattern_statistics.pdf
│
├── tests/                              # 🧪 测试目录（新增）
│   ├── __init__.py
│   ├── test_extractors.py
│   ├── test_rag.py
│   └── test_kg_builder.py
│
├── docs/                               # 📖 文档目录（新增）
│   ├── architecture.md                 # 架构设计
│   ├── api_reference.md                # API文档
│   ├── user_guide.md                   # 使用指南
│   └── schema_specification.md         # Schema规范
│
└── archive/                            # 🗄️ 归档目录（新增）
    ├── old_code/                       # 旧代码备份
    └── deprecated_results/             # 废弃结果
```

---

## 🎯 迁移计划

### 阶段1：结构重组（不影响现有代码运行）

1. **创建新目录结构**
   ```bash
   mkdir -p data/raw/papers/{priority,general}
   mkdir -p data/processed/{embeddings,extracted_kg}
   mkdir -p configs/{prompts,schemas,model_configs}
   mkdir -p src/{extraction,rag,data_processing,knowledge_graph,utils}
   mkdir -p scripts notebooks outputs/{results,logs,figures,reports} tests docs archive
   ```

2. **复制（不删除）关键文件**
   ```bash
   # 保持原文件不动，先复制到新位置测试
   cp -r 论文文献/* data/raw/papers/general/
   cp prompt/prompt.txt configs/prompts/extraction_prompt.txt
   cp schema文件/phm_semantic_patterns.json configs/schemas/
   ```

3. **逐步迁移代码**
   - 先重构 `code/抽取/` 到 `src/extraction/`
   - 测试无误后删除旧代码
   - 标记 `code/` 为 `archive/old_code/`

### 阶段2：代码模块化重构

1. **提取公共基类**
   - 创建 `BaseExtractor` 统一三个模型的接口
   - 将重复代码抽取到 `utils/`

2. **集成RAG功能**
   - 实现 `PatternRetriever`
   - 修改抽取器调用RAG检索

3. **添加配置管理**
   - 使用 YAML 配置文件替代硬编码
   - 支持命令行参数

### 阶段3：完善文档和测试

1. **编写README.md**
2. **添加单元测试**
3. **生成API文档**

---

## 📋 关键文件说明

### **必备文件**

#### `README.md` - 项目说明
```markdown
# PHM知识图谱抽取项目

## 简介
从航空航天PHM领域学术论文中自动抽取实体和关系，构建知识图谱。

## 快速开始
1. 环境配置: `conda env create -f environment.yml`
2. 构建向量库: `python scripts/01_build_vector_db.py`
3. 运行抽取: `python scripts/02_run_extraction.py`

## 目录结构
见 PROJECT_STRUCTURE.md

## 技术栈
- LangChain, ChromaDB, FAISS
- OpenAI, DeepSeek, Gemini, Kimi

## 文档
- 使用指南: docs/user_guide.md
- API文档: docs/api_reference.md
```

#### `requirements.txt` - Python依赖
```txt
langchain==0.3.27
langchain-community==0.3.31
langchain-core==0.3.79
langchain-openai==0.3.35
langchain-text-splitters==0.3.11
chromadb==1.1.1
faiss-cpu==1.12.0
openai==2.3.0
pandas>=2.0.0
pyyaml>=6.0
tqdm>=4.65.0
```

#### `environment.yml` - Conda环境
```yaml
name: phm_knowledge
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.11
  - pip
  - pip:
    - -r requirements.txt
```

#### `.gitignore` - Git忽略规则
```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/

# Data
data/raw/papers/*.md
data/processed/embeddings/
*.csv
*.json

# Outputs
outputs/logs/
outputs/results/
*.log

# API Keys
.env
*.key

# IDE
.vscode/
.idea/
*.swp
```

---

## 💡 科研项目组织的黄金原则

### 1. **分离原则**
- 📊 **数据** vs 💻 **代码** vs 📤 **结果** 严格分离
- 🔒 **原始数据只读**，处理结果单独存放
- 🧪 **实验代码** vs 🏭 **生产代码** 分开管理

### 2. **可复现原则**
- ✅ 所有依赖写入 `requirements.txt`
- ✅ 配置文件化（不要硬编码）
- ✅ 使用随机种子固定结果

### 3. **命名规范**
- 📁 目录名：`小写_下划线`（如 `data_processing`）
- 📄 Python文件：`小写_下划线.py`（如 `pattern_retriever.py`）
- 🏷️ 类名：`大驼峰`（如 `PatternRetriever`）
- 🔤 函数名：`小写_下划线`（如 `build_vector_db`）

### 4. **版本控制**
- 🔄 使用Git管理代码
- 📝 编写有意义的commit message
- 🏷️ 重要版本打tag（如 `v1.0-paper-submission`）

### 5. **文档优先**
- 📖 README.md 第一优先级
- 💬 代码注释要清晰
- 📚 复杂逻辑单独写文档

---

## 🎓 学习资源

### 优秀科研项目范例
1. [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
2. [ML Project Template](https://github.com/drivendata/cookiecutter-data-science)
3. [Research Project Template](https://github.com/mkrapp/cookiecutter-reproducible-science)

### 推荐阅读
- 《Good Enough Practices in Scientific Computing》
- 《The Turing Way: Guide for Reproducible Research》

---

## ✅ 下一步行动

1. **立即执行**：
   - [ ] 创建 `README.md`
   - [ ] 生成 `requirements.txt`
   - [ ] 创建新目录结构

2. **本周内完成**：
   - [ ] 重构抽取代码到 `src/extraction/`
   - [ ] 实现RAG模块 `src/rag/`
   - [ ] 编写第一个测试用例

3. **持续改进**：
   - [ ] 添加日志系统
   - [ ] 实现配置管理
   - [ ] 完善文档

---

**最后建议**：不要一次性重构所有代码！先建立新结构，逐步迁移，保持项目始终可运行。
