# 📁 PHM知识图谱项目 - 文件结构说明

> 本文档解释了项目的文件夹组织结构及其设计原理

## 🎯 项目结构设计原则

### 1. **分离原则** (Separation of Concerns)
- **数据** vs **代码** vs **配置** vs **输出** 分开管理
- 原始数据不可修改，处理结果独立存放

### 2. **可复现性** (Reproducibility)
- 明确的依赖管理 (`requirements.txt`, `environment.yml`)
- 版本控制友好的结构
- 完整的文档说明

### 3. **可扩展性** (Scalability)
- 模块化的代码组织
- 易于添加新功能和新模型
- 支持多实验并行

---

## 📂 当前项目结构

```
E:\langchain/                           # 项目根目录
│
├── README.md                            # 项目总览（必读！）
├── requirements.txt                     # Python依赖包列表
├── environment.yml                      # Conda环境配置
├── .gitignore                          # Git忽略规则
│
├── data/                               # 【数据目录】
│   ├── raw/                            # 原始数据（只读）
│   │   └── papers/                     # 原始论文文献
│   │       ├── priority/               # 优先处理的50篇论文
│   │       └── general/                # 其他论文
│   │
│   ├── processed/                      # 处理后的数据
│   │   └── dependency_patterns/        # 依存句法分析结果
│   │
│   └── vectordb/                       # 向量数据库
│       └── chroma_db/                  # ChromaDB持久化目录
│
├── configs/                            # 【配置文件目录】
│   ├── prompts/                        # Prompt模板
│   │   └── extraction_prompt.txt       # 实体关系抽取提示词
│   │
│   ├── schemas/                        # Schema定义
│   │   └── phm_semantic_patterns.json  # PHM语义模式
│   │
│   └── model_configs/                  # 模型配置
│       ├── deepseek.yaml
│       ├── gemini.yaml
│       └── kimi.yaml
│
├── src/                                # 【源代码目录】
│   ├── __init__.py
│   │
│   ├── extraction/                     # 实体关系抽取模块
│   │   ├── __init__.py
│   │   ├── main.py                     # 主控脚本
│   │   ├── extractors/                 # 各模型提取器
│   │   │   ├── __init__.py
│   │   │   ├── base_extractor.py       # 基类
│   │   │   ├── deepseek_extractor.py
│   │   │   ├── gemini_extractor.py
│   │   │   └── kimi_extractor.py
│   │   │
│   │   └── utils/                      # 工具函数
│   │       ├── __init__.py
│   │       ├── json_parser.py          # JSON解析
│   │       └── logger.py               # 日志工具
│   │
│   ├── rag/                            # RAG检索增强模块
│   │   ├── __init__.py
│   │   ├── pattern_vectorizer.py       # 模式向量化
│   │   ├── retriever.py                # 检索器
│   │   └── prompt_enhancer.py          # Prompt增强器
│   │
│   ├── metadata/                       # 元数据处理模块
│   │   ├── __init__.py
│   │   ├── fill_metadata.py            # 元数据填充
│   │   └── audit_metadata.py           # 元数据审计
│   │
│   └── utils/                          # 通用工具
│       ├── __init__.py
│       ├── file_utils.py               # 文件操作
│       └── api_utils.py                # API调用封装
│
├── scripts/                            # 【可执行脚本】
│   ├── 01_build_vectordb.py            # 构建向量数据库
│   ├── 02_run_extraction.py            # 运行知识抽取
│   ├── 03_evaluate_results.py          # 评估抽取结果
│   └── setup_environment.sh            # 环境配置脚本
│
├── outputs/                            # 【输出目录】
│   ├── extractions/                    # 抽取结果
│   │   ├── deepseek_experiment/        # DeepSeek模型结果
│   │   │   ├── in_scope/               # 前50篇
│   │   │   └── out_scope/              # 其他篇
│   │   ├── gemini_experiment/
│   │   └── kimi_experiment/
│   │
│   ├── logs/                           # 日志文件
│   │   ├── deepseek/
│   │   ├── gemini/
│   │   └── kimi/
│   │
│   ├── analysis/                       # 分析结果
│   │   ├── statistics/                 # 统计数据
│   │   └── visualizations/             # 可视化图表
│   │
│   └── knowledge_graph/                # 知识图谱
│       ├── entities.json               # 实体库
│       ├── relations.json              # 关系库
│       └── graph.neo4j                 # Neo4j图数据库
│
├── notebooks/                          # 【Jupyter笔记本】
│   ├── 01_data_exploration.ipynb       # 数据探索
│   ├── 02_pattern_analysis.ipynb       # 模式分析
│   ├── 03_rag_experiments.ipynb        # RAG实验
│   └── 04_evaluation.ipynb             # 结果评估
│
├── tests/                              # 【单元测试】
│   ├── __init__.py
│   ├── test_extractors.py
│   ├── test_rag.py
│   └── test_utils.py
│
└── docs/                               # 【文档】
    ├── PROJECT_STRUCTURE.md            # 本文件
    ├── SETUP_GUIDE.md                  # 安装配置指南
    ├── USER_MANUAL.md                  # 使用手册
    ├── API_REFERENCE.md                # API文档
    └── CHANGELOG.md                    # 更新日志
```

---

## 📝 重要文件说明

### 1. 配置文件

#### `requirements.txt`
```txt
# 项目Python依赖包列表
langchain==0.3.27
langchain-openai==0.3.35
langchain-community==0.3.31
chromadb==1.1.1
faiss-cpu==1.12.0
openai==2.3.0
...
```

#### `environment.yml`
```yaml
# Conda环境完整配置
name: phm_knowledge
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - pip:
    - -r requirements.txt
```

### 2. 数据组织

#### 原始数据 (`data/raw/`)
- **只读**：永不修改原始数据
- **版本控制**：大文件用 `.gitignore` 排除
- **文档化**：README说明数据来源

#### 处理数据 (`data/processed/`)
- **可再生**：可通过脚本重新生成
- **版本化**：用时间戳或版本号区分

### 3. 代码组织

#### 模块化原则
```python
# src/extraction/extractors/base_extractor.py
class BaseExtractor:
    """所有提取器的基类"""
    
    def extract(self, paper_text: str) -> dict:
        """抽取实体和关系"""
        raise NotImplementedError
```

```python
# src/extraction/extractors/deepseek_extractor.py
class DeepSeekExtractor(BaseExtractor):
    """DeepSeek模型提取器"""
    
    def extract(self, paper_text: str) -> dict:
        # 具体实现
        pass
```

---

## 🔄 工作流程

### 阶段1：环境准备
```bash
# 1. 创建conda环境
conda env create -f environment.yml
conda activate phm_knowledge

# 2. 验证安装
python -c "import langchain; print(langchain.__version__)"
```

### 阶段2：数据准备
```bash
# 1. 构建向量数据库
python scripts/01_build_vectordb.py

# 2. 验证向量库
python -c "from src.rag import test_retrieval; test_retrieval()"
```

### 阶段3：知识抽取
```bash
# 运行抽取流程（三个模型串行）
python scripts/02_run_extraction.py
```

### 阶段4：结果分析
```bash
# 评估抽取质量
python scripts/03_evaluate_results.py

# 或使用Jupyter Notebook交互式分析
jupyter notebook notebooks/04_evaluation.ipynb
```

---

## 🎓 学习路径建议

### 对于代码新手：

1. **先理解结构**
   - 阅读本文档
   - 查看 `README.md` 了解项目目标
   
2. **从配置入手**
   - 查看 `configs/` 目录下的配置文件
   - 理解Prompt和Schema的作用
   
3. **跟踪数据流**
   - 原始论文 → 向量化 → 检索 → Prompt增强 → LLM抽取 → 结构化输出
   
4. **逐步学习代码**
   - 从工具函数开始 (`src/utils/`)
   - 理解基类设计 (`src/extraction/extractors/base_extractor.py`)
   - 学习具体实现 (各个extractor)
   
5. **实践与实验**
   - 在 `notebooks/` 中做小实验
   - 修改配置看效果变化
   - 尝试添加新功能

---

## 📚 扩展阅读

- [LangChain官方文档](https://python.langchain.com/)
- [RAG技术详解](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [科研项目管理最佳实践](https://goodresearch.dev/)
- [Python项目结构指南](https://realpython.com/python-application-layouts/)

---

## ❓ 常见问题

**Q: 为什么要分 `src/` 和 `scripts/`？**  
A: `src/` 是可重用的模块（库代码），`scripts/` 是面向任务的脚本（应用代码）。

**Q: 数据应该放在哪里？**  
A: 原始数据 → `data/raw/`，处理后数据 → `data/processed/`，输出结果 → `outputs/`。

**Q: 如何添加新的LLM模型？**  
A: 在 `src/extraction/extractors/` 创建新类，继承 `BaseExtractor`，实现 `extract()` 方法。

---

*最后更新：2025-10-14*
