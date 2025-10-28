# 🎓 新手学习指南 - 如何理解科研项目的文件结构

> 专为编程新手设计的学习路径

## 📚 目录
1. [为什么要组织文件结构？](#1-为什么要组织文件结构)
2. [科研项目的通用结构](#2-科研项目的通用结构)
3. [本项目的结构详解](#3-本项目的结构详解)
4. [实践练习](#4-实践练习)
5. [常见错误与最佳实践](#5-常见错误与最佳实践)

---

## 1. 为什么要组织文件结构？

### 🤔 想象一个场景

**糟糕的组织方式:**
```
我的项目/
├── 论文1.md
├── 论文2.md
├── 代码.py
├── 代码2.py
├── 代码-最终版.py
├── 代码-最终版-真的最终版.py
├── 结果.json
├── 结果2.json
├── 不知道什么.txt
└── 新建文件夹/
    └── 随便放的东西/
```

❌ **问题:**
- 找不到文件在哪
- 不知道哪个是最新版本
- 团队合作时一团糟
- 三个月后你自己都看不懂

**良好的组织方式:**
```
我的项目/
├── data/          # 📊 数据在这
│   ├── raw/       # 原始数据
│   └── processed/ # 处理后数据
├── src/           # 💻 代码在这
│   ├── models/
│   └── utils/
├── outputs/       # 📁 结果在这
│   ├── reports/
│   └── figures/
└── README.md      # 📖 说明在这
```

✅ **优点:**
- 一目了然，快速定位
- 逻辑清晰，易于理解
- 方便协作和分享
- 半年后回来还能看懂

---

## 2. 科研项目的通用结构

### 📦 核心原则：按"功能"分类，而非随意堆放

```
project/
│
├── 📊 data/           # 【数据层】存放所有数据
│   ├── raw/           # 原始数据（不改动）
│   ├── processed/     # 处理后数据（可再生成）
│   └── external/      # 外部数据源
│
├── 💻 src/            # 【代码层】可重用的代码模块
│   ├── models/        # 模型定义
│   ├── utils/         # 工具函数
│   └── __init__.py    # Python包标识
│
├── 🚀 scripts/        # 【脚本层】一次性运行的脚本
│   ├── train.py       # 训练脚本
│   └── evaluate.py    # 评估脚本
│
├── ⚙️ configs/        # 【配置层】配置文件
│   ├── config.yaml    # 主配置
│   └── model.json     # 模型参数
│
├── 📁 outputs/        # 【输出层】所有输出结果
│   ├── models/        # 训练好的模型
│   ├── logs/          # 日志文件
│   └── figures/       # 图表
│
├── 📓 notebooks/      # 【探索层】实验和分析
│   └── *.ipynb        # Jupyter笔记本
│
├── 📖 docs/           # 【文档层】说明文档
│   ├── guide.md
│   └── api.md
│
├── 🧪 tests/          # 【测试层】单元测试
│   └── test_*.py
│
└── 📋 README.md       # 项目总览（必备！）
```

---

## 3. 本项目的结构详解

### 🗺️ 完整导览图

```
E:\langchain/
│
├── 📋 README.md              ← 【从这里开始！】项目说明
├── 📦 requirements.txt       ← 需要安装的Python包
├── 🐍 environment.yml        ← Conda环境配置
│
├── 📊 data/                  ← 【1. 数据存储区】
│   ├── raw/                  ← 原始数据（只读，绝不修改）
│   │   └── papers/           ← 200篇PHM论文
│   │       ├── priority/     ← 优先处理的50篇
│   │       └── general/      ← 其余论文
│   │
│   ├── processed/            ← 处理后的数据（可重新生成）
│   │   └── dependency_patterns/  ← 依存句法分析结果CSV
│   │
│   └── vectordb/             ← 向量数据库（RAG用）
│       └── chroma_db/        ← ChromaDB文件
│
├── ⚙️ configs/               ← 【2. 配置文件区】
│   ├── prompts/              ← Prompt模板
│   │   └── extraction_prompt.txt  ← 实体关系抽取提示词
│   │
│   ├── schemas/              ← Schema定义
│   │   └── phm_semantic_patterns.json  ← 模式库
│   │
│   └── model_configs/        ← 各模型的配置
│       ├── deepseek.yaml
│       ├── gemini.yaml
│       └── kimi.yaml
│
├── 💻 src/                   ← 【3. 源代码区】（可重用的模块）
│   ├── extraction/           ← 知识抽取模块
│   │   ├── main.py           ← 主控程序
│   │   ├── extractors/       ← 各模型的提取器
│   │   │   ├── base_extractor.py      ← 基类（父类）
│   │   │   ├── deepseek_extractor.py  ← DeepSeek实现
│   │   │   ├── gemini_extractor.py    ← Gemini实现
│   │   │   └── kimi_extractor.py      ← Kimi实现
│   │   └── utils/            ← 工具函数
│   │
│   ├── rag/                  ← RAG检索增强模块
│   │   ├── pattern_vectorizer.py   ← 向量化器
│   │   ├── retriever.py            ← 检索器
│   │   └── prompt_enhancer.py      ← Prompt增强器
│   │
│   └── utils/                ← 通用工具
│       ├── file_utils.py     ← 文件操作
│       └── api_utils.py      ← API调用
│
├── 🚀 scripts/               ← 【4. 执行脚本区】（直接运行的程序）
│   ├── 01_build_vectordb.py      ← 第1步：构建向量库
│   ├── 02_run_extraction.py      ← 第2步：运行抽取
│   └── 03_evaluate_results.py    ← 第3步：评估结果
│
├── 📁 outputs/               ← 【5. 输出结果区】
│   ├── extractions/          ← 抽取结果（JSON）
│   │   ├── deepseek_experiment/
│   │   ├── gemini_experiment/
│   │   └── kimi_experiment/
│   │
│   ├── logs/                 ← 运行日志
│   │   ├── deepseek/
│   │   ├── gemini/
│   │   └── kimi/
│   │
│   └── knowledge_graph/      ← 最终知识图谱
│       ├── entities.json     ← 实体库
│       └── relations.json    ← 关系库
│
├── 📓 notebooks/             ← 【6. 实验笔记区】
│   ├── 01_data_exploration.ipynb    ← 数据探索
│   ├── 02_pattern_analysis.ipynb   ← 模式分析
│   └── 03_rag_experiments.ipynb    ← RAG实验
│
├── 🧪 tests/                 ← 【7. 测试代码区】
│   ├── test_extractors.py
│   └── test_rag.py
│
└── 📖 docs/                  ← 【8. 文档区】
    ├── PROJECT_STRUCTURE.md      ← 结构说明
    ├── BEGINNER_GUIDE.md         ← 本文件
    ├── SETUP_GUIDE.md            ← 安装指南
    └── USER_MANUAL.md            ← 使用手册
```

---

## 4. 实践练习

### 🎯 练习1：理解层次关系

**问题:** 以下文件应该放在哪里？

1. 一篇新下载的PHM论文 PDF
2. 训练DeepSeek模型的Python脚本
3. 数据分析的Jupyter笔记本
4. 提取出的实体关系JSON结果
5. API密钥配置文件

<details>
<summary>点击查看答案</summary>

1. `data/raw/papers/general/` （原始数据）
2. `scripts/train_deepseek.py` （可执行脚本）
3. `notebooks/data_analysis.ipynb` （实验笔记）
4. `outputs/extractions/deepseek_experiment/` （输出结果）
5. `.env` 文件（根目录，不提交到Git）

</details>

### 🎯 练习2：追踪数据流

**问题:** 一篇论文经历了哪些阶段？

```
论文.md → ？ → ？ → ？ → 实体关系.json
```

<details>
<summary>点击查看答案</summary>

```
1. 论文.md (data/raw/papers/)
   ↓
2. 向量化存入数据库 (data/vectordb/chroma_db/)
   ↓
3. RAG检索相似模式 (src/rag/retriever.py)
   ↓
4. 增强Prompt (src/rag/prompt_enhancer.py)
   ↓
5. LLM抽取 (src/extraction/extractors/*.py)
   ↓
6. 实体关系.json (outputs/extractions/)
```

</details>

### 🎯 练习3：代码组织

**问题:** 以下代码应该放在 `src/` 还是 `scripts/`？

1. 一个可以被多个脚本调用的JSON解析函数
2. 一个运行完整抽取流程的主程序
3. DeepSeek提取器的实现类
4. 一个测试向量检索功能的小程序

<details>
<summary>点击查看答案</summary>

1. `src/utils/json_parser.py` （可重用工具）
2. `scripts/02_run_extraction.py` （面向任务的脚本）
3. `src/extraction/extractors/deepseek_extractor.py` （可重用模块）
4. `scripts/test_retrieval.py` 或 `notebooks/test_retrieval.ipynb` （一次性测试）

**判断标准:**
- 会被多次调用？→ `src/`
- 只运行一次？→ `scripts/` 或 `notebooks/`

</details>

---

## 5. 常见错误与最佳实践

### ❌ 常见错误

#### 错误1：所有文件堆在根目录
```
项目/
├── 论文1.md
├── 论文2.md
├── 代码1.py
├── 代码2.py
├── 结果1.json
└── ...一百个文件...
```
**为什么错？** 找不到任何东西，无法维护。

#### 错误2：中文文件夹名+空格
```
项目/
└── 我的 代码 文件夹/
```
**为什么错？** 命令行不友好，跨平台有问题。

#### 错误3：重要配置在代码中硬编码
```python
API_KEY = "sk-abc123..."  # ❌ 泄露风险
file_path = "C:/Users/张三/Desktop/..."  # ❌ 别人无法运行
```

#### 错误4：原始数据和结果混在一起
```
data/
├── paper1_original.md  # 原始
├── paper1_cleaned.md   # 处理后
└── paper1_result.json  # 结果
```
**为什么错？** 分不清哪个是源头，哪个是输出。

### ✅ 最佳实践

#### 实践1：使用英文+下划线命名
```
good_folder_name/
├── data_processing.py
└── model_config.json
```

#### 实践2：配置与代码分离
```python
# ✅ 从环境变量读取
import os
API_KEY = os.getenv("OPENAI_API_KEY")
```

```bash
# .env 文件（不提交到Git）
OPENAI_API_KEY=sk-abc123...
```

#### 实践3：数据分层
```
data/
├── raw/        # 原始数据（只读）
├── processed/  # 处理后数据（可重新生成）
└── vectordb/   # 向量库（可重建）
```

#### 实践4：文档化一切
- 每个目录有 `README.md` 说明用途
- 代码有注释说明为什么这样做
- 项目根目录的 `README.md` 是入口

#### 实践5：版本控制友好
```
.gitignore      # 忽略不需要提交的文件
├── data/       # 大文件不提交
├── outputs/    # 临时结果不提交
├── *.log       # 日志不提交
└── .env        # 密钥不提交
```

---

## 📝 学习路径

### 阶段1：理解（1-2天）
1. 阅读本文档 ✓
2. 查看项目的实际文件结构
3. 理解每个目录的作用

### 阶段2：模仿（3-5天）
1. 尝试将自己的其他项目按此结构整理
2. 创建新项目时遵循这个模板
3. 观察别人的开源项目结构

### 阶段3：内化（1-2周）
1. 形成自己的组织习惯
2. 根据项目特点灵活调整
3. 能够向他人解释为什么这样组织

---

## 🔗 延伸阅读

### 入门级
- [GitHub Guide: Getting Started](https://guides.github.com/)
- [Python项目结构最佳实践](https://realpython.com/python-application-layouts/)

### 进阶级
- [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
- [Good Research Code Handbook](https://goodresearch.dev/)

### 本项目专属
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 详细结构说明
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 环境配置指南
- [USER_MANUAL.md](USER_MANUAL.md) - 使用手册

---

## ❓ 答疑时间

**Q: 我必须完全遵循这个结构吗？**  
A: 不必须，但这是经过验证的最佳实践。小项目可以简化，大项目可能需要更细分。

**Q: 如果我的项目很小，也要这么复杂吗？**  
A: 小项目可以简化：
```
small_project/
├── data/
├── src/
├── outputs/
└── README.md
```

**Q: 文件夹太多了，记不住怎么办？**  
A: 不需要记！打开 `docs/PROJECT_STRUCTURE.md` 查看即可。习惯后自然就记住了。

**Q: 我改了结构，代码会不会崩？**  
A: 可能会。建议：
1. 先备份（运行 `python scripts/reorganize_project.py`）
2. 更新代码中的路径
3. 使用相对路径而非绝对路径

---

## 🎉 总结

好的文件结构就像整洁的书桌：
- ✅ 让你快速找到需要的东西
- ✅ 让你的工作更有效率
- ✅ 让别人能理解你的工作
- ✅ 让未来的你感谢现在的你

**记住三个关键词:**
1. **分层** - 按功能分类
2. **命名** - 清晰且一致
3. **文档** - 说明每个部分的用途

---

*祝你学习愉快！有问题欢迎提Issue* 😊

*最后更新：2025-10-14*
