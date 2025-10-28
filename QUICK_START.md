# 🚀 快速整理指南

> 三步完成项目文件整理

## 📋 整理前检查清单

- [ ] 已备份重要数据
- [ ] 已安装Python 3.10+
- [ ] 已激活 `phm_knowledge` conda环境

## 🎯 三步整理法

### 步骤1：预览整理计划（安全模式）

```powershell
# 在项目根目录执行
cd E:\langchain

# 预览将要进行的操作（不会实际修改文件）
python scripts/reorganize_project.py --dry-run
```

**输出示例:**
```
==============================================================
🔧 PHM项目文件结构重组工具
==============================================================

⚠️  DRY RUN 模式 - 仅预览，不实际修改文件

[预览] 将创建备份目录
📁 创建新目录结构...
[预览] 将创建标准项目结构

[预览] 将移动以下文件:
  - 论文文献 -> data/raw/papers/
  - 依存路径提取结果 -> data/processed/
  - prompt -> configs/prompts/
  - schema文件 -> configs/schemas/
  - code/ -> src/

[预览] 将创建配置文件:
  - .gitignore
  - .env.example
  - README.md

==============================================================
✅ 预览完成！如需实际执行，请去掉 --dry-run 参数
==============================================================
```

### 步骤2：执行整理（正式操作）

```powershell
# 确认无误后，正式执行
python scripts/reorganize_project.py
```

**执行过程:**
1. ✅ 自动创建备份目录（`_backup_YYYYMMDD_HHMMSS/`）
2. ✅ 创建新的标准目录结构
3. ✅ 复制文件到新位置
4. ✅ 生成配置文件模板
5. ✅ 更新README文档

**完成提示:**
```
==============================================================
✅ 项目重组完成！
📦 备份位置: E:\langchain\_backup_20251014_153045

📖 下一步:
  1. 检查 docs/PROJECT_STRUCTURE.md 了解新结构
  2. 配置 .env 文件
  3. 运行 python scripts/01_build_vectordb.py
==============================================================
```

### 步骤3：验证新结构

```powershell
# 查看新的目录树
tree /F E:\langchain

# 或使用Python查看
python -c "import os; os.system('tree /F')"
```

---

## 📁 整理后的对照表

| 旧位置 | 新位置 | 说明 |
|--------|--------|------|
| `论文文献/需要评估的论文/` | `data/raw/papers/priority/` | 优先论文 |
| `论文文献/*.md` | `data/raw/papers/general/` | 其他论文 |
| `依存路径提取结果/` | `data/processed/dependency_patterns/` | 分析结果 |
| `prompt/` | `configs/prompts/` | Prompt模板 |
| `schema文件/` | `configs/schemas/` | Schema定义 |
| `code/抽取/` | `src/extraction/extractors/` | 抽取代码 |
| `code/rag/` | `src/rag/` | RAG模块 |
| `code/填充脚本/` | `src/metadata/` | 元数据处理 |

---

## 🔧 手动微调（可选）

整理完成后，你可能需要手动调整：

### 1. 更新代码中的路径

**before:**
```python
PAPERS_DIR = os.path.join(ROOT_DIR, "论文文献")
```

**after:**
```python
PAPERS_DIR = os.path.join(ROOT_DIR, "data", "raw", "papers")
```

### 2. 配置环境变量

```powershell
# 复制模板
copy .env.example .env

# 编辑 .env 文件，填入你的API Keys
notepad .env
```

### 3. 删除旧文件（确认无误后）

```powershell
# ⚠️ 警告：确保备份完整后再执行！
Remove-Item "E:\langchain\code" -Recurse -Force
Remove-Item "E:\langchain\prompt" -Recurse -Force
Remove-Item "E:\langchain\schema文件" -Recurse -Force
Remove-Item "E:\langchain\论文文献" -Recurse -Force
Remove-Item "E:\langchain\依存路径提取结果" -Recurse -Force
```

---

## 📚 学习资源链接

整理完成后，按顺序阅读：

1. **[新手指南](docs/BEGINNER_GUIDE.md)** ← 从这里开始
   - 理解为什么要这样组织
   - 学习科研项目的标准结构
   - 实践练习和常见错误

2. **[结构说明](docs/PROJECT_STRUCTURE.md)**
   - 详细的目录结构文档
   - 每个文件夹的作用
   - 工作流程图

3. **[配置指南](docs/SETUP_GUIDE.md)**
   - 环境配置步骤
   - API Key设置
   - 依赖安装

4. **[使用手册](docs/USER_MANUAL.md)**
   - 如何运行项目
   - 常见问题解答
   - 最佳实践

---

## ⚠️ 注意事项

### 如果整理过程出错

1. **不要慌！** 你的原始文件已备份在 `_backup_*` 目录

2. **恢复备份:**
   ```powershell
   # 找到最新的备份目录
   $backup = Get-ChildItem -Path "E:\langchain" -Filter "_backup_*" | 
             Sort-Object Name -Descending | Select-Object -First 1
   
   # 查看备份内容
   tree /F $backup.FullName
   
   # 手动恢复需要的文件
   ```

3. **重新开始:**
   ```powershell
   # 删除新创建的目录
   Remove-Item "E:\langchain\data" -Recurse -Force
   Remove-Item "E:\langchain\configs" -Recurse -Force
   Remove-Item "E:\langchain\src" -Recurse -Force
   # ... 其他新目录
   
   # 从备份恢复
   Copy-Item -Path "$($backup.FullName)\*" -Destination "E:\langchain\" -Recurse
   ```

---

## 🎉 完成！

整理完成后，你的项目将拥有：

- ✅ 清晰的目录结构
- ✅ 标准的命名规范
- ✅ 完整的文档说明
- ✅ 易于维护和扩展

**下一步：**

```powershell
# 1. 查看新结构
cd E:\langchain
tree /F

# 2. 阅读文档
start docs\BEGINNER_GUIDE.md

# 3. 配置环境
copy .env.example .env
notepad .env

# 4. 构建向量库
python scripts\01_build_vectordb.py
```

---

## 📞 需要帮助？

- 📖 查看 [docs/](docs/) 目录下的详细文档
- 🐛 遇到Bug？提交Issue
- 💬 有疑问？查看FAQ或提问

---

*祝你整理顺利！* 🎊
