# 🚀 PHM知识图谱项目

> 基于LangChain和RAG技术的航空PHM领域知识图谱自动构建系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.27-green.svg)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

本项目旨在从航空航天领域的PHM（预测与健康管理，Prognostics and Health Management）学术文献中**自动抽取实体和关系**，构建领域知识图谱。

### 🎯 核心功能

- **📄 文献处理**: 处理200+篇PHM领域学术论文
- **🤖 多模型抽取**: 支持DeepSeek、Gemini、Kimi三种LLM模型
- **🔍 RAG增强**: 基于依存句法分析的模式检索增强
- **📊 知识图谱**: 自动构建实体-关系知识图谱
- **💾 向量检索**: ChromaDB向量数据库支持

---

## 🌟 特色亮点

1. **Schema驱动**: 基于PHM领域专业Schema进行抽取
2. **模式学习**: 从2287条依存句法模式中学习
3. **RAG技术**: 动态检索最相关的抽取模式示例
4. **多模型对比**: 三个模型并行抽取，结果可对比分析
5. **断点续传**: 支持中断后继续，不重复处理

---

## 🚀 快速开始

### 方案A：新手整理方案（推荐）

如果你是**代码新手**或想**学习项目组织**，请按以下步骤：

```powershell
# 1. 查看整理指南（了解科研项目如何组织）
notepad QUICK_START.md

# 2. 预览整理效果（安全模式，不修改文件）
python scripts/reorganize_project.py --dry-run

# 3. 确认无误后，正式整理
python scripts/reorganize_project.py

# 4. 学习项目结构
notepad docs/BEGINNER_GUIDE.md
```

### 方案B：快速运行方案

如果你已经熟悉项目结构，可以直接运行：

```bash
# 1. 激活环境
conda activate phm_knowledge

# 2. 配置API Keys
copy .env.example .env
notepad .env  # 填入你的API密钥

# 3. 构建向量数据库
python scripts/01_build_vectordb.py

# 4. 运行知识抽取
python scripts/02_run_extraction.py
```

---

## 📁 项目结构

```
E:\langchain/
├── 📊 data/              # 数据（论文、向量库）
├── ⚙️ configs/          # 配置（Prompt、Schema）
├── 💻 src/              # 源代码（模块化）
├── 🚀 scripts/          # 可执行脚本
├── 📁 outputs/          # 输出结果
├── 📓 notebooks/        # Jupyter实验
├── 🧪 tests/            # 单元测试
└── 📖 docs/             # 文档
```

**详细说明:** [📂 查看完整结构文档](docs/PROJECT_STRUCTURE.md)

---

## 📚 学习路径

### 👶 对于新手

**第1天 - 理解项目**
1. 阅读 [QUICK_START.md](QUICK_START.md) - 3步整理指南
2. 学习 [docs/BEGINNER_GUIDE.md](docs/BEGINNER_GUIDE.md) - 新手教程
3. 理解 [docs/STRUCTURE_COMPARISON.md](docs/STRUCTURE_COMPARISON.md) - 前后对比

**第2天 - 配置环境**
1. 按照 [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) 配置环境
2. 运行 `python scripts/reorganize_project.py --dry-run` 预览
3. 执行整理并查看新结构

**第3天 - 运行项目**
1. 构建向量数据库
2. 运行知识抽取
3. 查看输出结果

### 🎓 对于有经验者

直接查看：
- [📖 API文档](docs/API_REFERENCE.md)
- [💻 代码结构](src/)
- [🔧 配置说明](configs/)

---

## 🎯 核心技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10+ | 开发语言 |
| **LangChain** | 0.3.27 | LLM框架 |
| **ChromaDB** | 1.1.1 | 向量数据库 |
| **FAISS** | 1.12.0 | 向量检索 |
| **OpenAI API** | 2.3.0 | LLM调用 |

---

## 📊 数据统计

- 📄 **论文数量**: 200+ 篇
- 🔤 **抽取模式**: 2287 条依存句法模式
- 🏷️ **实体类型**: 30+ 种
- 🔗 **关系类型**: 25+ 种
- 🤖 **支持模型**: DeepSeek, Gemini, Kimi

---

## 🔄 工作流程

```
论文(MD) → 向量化 → RAG检索 → Prompt增强 → LLM抽取 → JSON输出
   ↓           ↓          ↓            ↓            ↓           ↓
data/raw  data/vectordb  src/rag  configs/prompts  src/extraction  outputs/
```

---

## 📚 完整文档导航

### 📖 入门文档
- [🚀 快速开始](QUICK_START.md) - 3步完成项目整理
- [🎓 新手指南](docs/BEGINNER_GUIDE.md) - 学习科研项目组织
- [📊 结构对比](docs/STRUCTURE_COMPARISON.md) - 整理前后对比

### 🔧 配置文档
- [⚙️ 环境配置](docs/SETUP_GUIDE.md) - 详细安装步骤
- [🔑 API配置](.env.example) - API密钥配置模板

### 📘 使用文档
- [📂 项目结构](docs/PROJECT_STRUCTURE.md) - 完整目录说明
- [📖 使用手册](docs/USER_MANUAL.md) - 功能使用指南
- [💻 API参考](docs/API_REFERENCE.md) - 代码接口文档

### 📝 更新日志
- [📜 CHANGELOG](docs/CHANGELOG.md) - 版本更新历史

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📧 联系方式

- 💬 **问题反馈**: [提交Issue](../../issues)
- 📝 **功能建议**: [提交Feature Request](../../issues/new)
- 📧 **邮件联系**: [联系维护者]

---

## 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- LangChain 团队提供的优秀框架
- OpenAI、DeepSeek、Gemini、Kimi 提供的API服务
- 所有贡献者的支持

---

## 📈 项目统计

![项目状态](https://img.shields.io/badge/Status-Active-success.svg)
![代码规范](https://img.shields.io/badge/Code%20Style-PEP8-blue.svg)
![文档完整](https://img.shields.io/badge/Documentation-Complete-brightgreen.svg)

---

**⭐ 如果这个项目对你有帮助，请给个Star！**

---

*最后更新：2025-10-14*
