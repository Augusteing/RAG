# -*- coding: utf-8 -*-
"""
基于 LangChain 的 PHM 依存路径模式向量数据库构建
使用 LangChain 标准组件：HuggingFaceEmbeddings + Chroma + Retriever
"""
import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# LangChain 核心组件
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 80)
print("🔧 PHM 依存路径模式向量数据库 (LangChain 版本)")
print("=" * 80)

# ==================== 配置部分 ====================

# 路径配置
CSV_FILE = PROJECT_ROOT / "data" / "processed" / "dependency_patterns" / "semantic_syntactic_patterns_report_2025-10-14_172830.csv"
CHROMA_PERSIST_DIR = str(PROJECT_ROOT / "data" / "vectorstores" / "langchain_chroma_db")
COLLECTION_NAME = "phm_dependency_patterns_langchain"

# LangChain Embedding 配置
EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"
EMBEDDING_DEVICE = "cuda"  # 或 "cpu"

# 测试模式
TEST_MODE = os.getenv("TEST_MODE", "0") == "1"
TEST_SAMPLE_SIZE = 20

print(f"\n📂 配置:")
print(f"   CSV 文件: {CSV_FILE.name}")
print(f"   向量库路径: {CHROMA_PERSIST_DIR}")
print(f"   Embedding 模型: {EMBEDDING_MODEL}")
print(f"   运行设备: {EMBEDDING_DEVICE}")
print(f"   测试模式: {'是' if TEST_MODE else '否'}")

# ==================== Step 1: 初始化 LangChain Embeddings ====================

print("\n" + "=" * 80)
print("Step 1: 初始化 LangChain HuggingFaceEmbeddings")
print("=" * 80)

# 创建 LangChain 的 HuggingFaceEmbeddings
# 这会自动使用 sentence-transformers 库
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': EMBEDDING_DEVICE},
    encode_kwargs={
        'normalize_embeddings': True,  # 归一化向量（余弦相似度友好）
        'batch_size': 32,              # 批处理大小
    }
)

print(f"✅ LangChain Embeddings 初始化完成")
print(f"   类型: {type(embeddings).__name__}")
print(f"   底层模型: {EMBEDDING_MODEL}")

# 测试 embedding
test_text = "深度学习模型预测设备故障"
test_embedding = embeddings.embed_query(test_text)
print(f"\n🧪 测试 Embedding:")
print(f"   文本: {test_text}")
print(f"   向量维度: {len(test_embedding)}")
print(f"   前5维: {test_embedding[:5]}")

# ==================== Step 2: 加载和准备数据 ====================

print("\n" + "=" * 80)
print("Step 2: 加载依存路径模式数据")
print("=" * 80)

def load_patterns_as_langchain_documents(csv_path: Path, test_mode: bool = False) -> List[Document]:
    """加载 CSV 数据并转换为 LangChain Document 格式"""
    
    # 读取 CSV
    df = pd.read_csv(csv_path)
    
    # 标准化列名
    column_mapping = {}
    for col in df.columns:
        if "语义模式" in col:
            column_mapping[col] = "语义模式"
        elif "总频次" in col or "频次" in col:
            column_mapping[col] = "总频次"
        elif "句法" in col and "路径" in col:
            column_mapping[col] = "句法实现路径"
    
    df = df.rename(columns=column_mapping)
    
    print(f"✅ 加载成功: {len(df)} 条模式")
    
    if test_mode:
        df = df.head(TEST_SAMPLE_SIZE)
        print(f"⚠️ 测试模式：仅处理前 {TEST_SAMPLE_SIZE} 条")
    
    # 转换为 LangChain Document
    documents = []
    for idx, row in df.iterrows():
        # 文档内容（用于向量化和检索）
        page_content = f"{row['语义模式']} | 句法路径: {row['句法实现路径']}"
        
        # 元数据（用于过滤和展示）
        metadata = {
            "pattern_id": str(idx),
            "semantic_pattern": row['语义模式'],
            "syntactic_path": row['句法实现路径'],
            "frequency": int(row['总频次']),
            "source": "dependency_parsing",
            "created_at": datetime.now().isoformat()
        }
        
        documents.append(Document(
            page_content=page_content,
            metadata=metadata
        ))
    
    print(f"✅ 转换完成: {len(documents)} 个 LangChain Documents")
    return documents

documents = load_patterns_as_langchain_documents(CSV_FILE, test_mode=TEST_MODE)

# 显示示例
print(f"\n📄 Document 示例:")
print(f"   内容: {documents[0].page_content[:80]}...")
print(f"   元数据: {documents[0].metadata}")

# ==================== Step 3: 构建 LangChain Chroma 向量库 ====================

print("\n" + "=" * 80)
print("Step 3: 构建 LangChain Chroma 向量数据库")
print("=" * 80)

# 删除旧数据库（如果存在）
import shutil
if os.path.exists(CHROMA_PERSIST_DIR):
    shutil.rmtree(CHROMA_PERSIST_DIR)
    print(f"   ℹ️ 已删除旧数据库: {CHROMA_PERSIST_DIR}")

# 创建 Chroma 向量库（LangChain 方式）
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory=CHROMA_PERSIST_DIR,
    collection_name=COLLECTION_NAME,
    collection_metadata={
        "description": "PHM 依存路径模式向量库 (LangChain)",
        "embedding_model": EMBEDDING_MODEL,
        "total_documents": len(documents),
        "created_at": datetime.now().isoformat()
    }
)

print(f"✅ Chroma 向量数据库构建完成")
print(f"   存储路径: {CHROMA_PERSIST_DIR}")
print(f"   Collection: {COLLECTION_NAME}")
print(f"   文档数量: {len(documents)}")

# 持久化到磁盘
vectorstore.persist()
print(f"✅ 数据库已持久化到磁盘")

# ==================== Step 4: 创建 LangChain Retriever ====================

print("\n" + "=" * 80)
print("Step 4: 创建 LangChain Retriever")
print("=" * 80)

# 创建检索器（支持多种检索策略）
retriever = vectorstore.as_retriever(
    search_type="similarity",  # 或 "mmr"（最大边际相关性）
    search_kwargs={
        "k": 5,  # 返回 Top-5 相似文档
        # "filter": {"frequency": {"$gt": 5}},  # 可选：按元数据过滤
    }
)

print(f"✅ Retriever 创建完成")
print(f"   检索策略: similarity")
print(f"   Top-K: 5")

# ==================== Step 5: 测试 LangChain RAG 检索 ====================

print("\n" + "=" * 80)
print("Step 5: 测试 LangChain RAG 检索")
print("=" * 80)

test_queries = [
    "深度学习模型预测设备故障",
    "传感器数据用于健康监测",
    "算法提升诊断准确率"
]

for query in test_queries:
    print(f"\n{'='*70}")
    print(f"🔍 查询: {query}")
    print(f"{'='*70}")
    
    # 使用 LangChain Retriever 检索
    retrieved_docs = retriever.get_relevant_documents(query)
    
    print(f"\n✅ 检索到 {len(retrieved_docs)} 个相关模式:")
    for i, doc in enumerate(retrieved_docs, 1):
        metadata = doc.metadata
        print(f"\n   [{i}] {metadata['semantic_pattern']}")
        print(f"       频次: {metadata['frequency']}")
        print(f"       句法路径: {metadata['syntactic_path'][:100]}...")
        
        # 计算相似度分数（如果需要）
        # score = vectorstore.similarity_search_with_score(query, k=1)[0][1]
        # print(f"       相似度: {score:.4f}")

# ==================== Step 6: 演示如何加载已有数据库 ====================

print("\n" + "=" * 80)
print("Step 6: 演示如何加载已有 LangChain 向量数据库")
print("=" * 80)

print(f"\n📝 在其他脚本中加载向量库的代码:")
print(f"""
```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. 重新初始化相同的 Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="{EMBEDDING_MODEL}",
    model_kwargs={{'device': '{EMBEDDING_DEVICE}'}},
    encode_kwargs={{'normalize_embeddings': True}}
)

# 2. 加载已有向量库
vectorstore = Chroma(
    persist_directory="{CHROMA_PERSIST_DIR}",
    embedding_function=embeddings,
    collection_name="{COLLECTION_NAME}"
)

# 3. 创建 Retriever
retriever = vectorstore.as_retriever(
    search_kwargs={{"k": 5}}
)

# 4. 使用 Retriever
query = "你的查询文本"
docs = retriever.get_relevant_documents(query)

# 5. 提取模式用于 Prompt
patterns = [doc.metadata['semantic_pattern'] for doc in docs]
```
""")

# ==================== 总结 ====================

print("\n" + "=" * 80)
print("✅ LangChain RAG 向量数据库构建完成！")
print("=" * 80)

print(f"\n📊 统计信息:")
print(f"   - 模式总数: {len(documents)}")
print(f"   - 向量维度: {len(test_embedding)}")
print(f"   - 存储路径: {CHROMA_PERSIST_DIR}")
print(f"   - Collection: {COLLECTION_NAME}")

print(f"\n🎯 LangChain 优势:")
print(f"   ✅ 标准化接口: 符合论文引用规范")
print(f"   ✅ 可替换组件: 轻松切换 Embedding/VectorStore")
print(f"   ✅ 高级检索: 支持 MMR、过滤、重排序")
print(f"   ✅ 集成性强: 与 LangChain 生态无缝对接")

print(f"\n💡 与之前方法的区别:")
print(f"   之前: SentenceTransformer + ChromaDB 原生 API")
print(f"   现在: LangChain HuggingFaceEmbeddings + Chroma (LangChain)")
print(f"   优势: 更标准、更易维护、论文可引用 LangChain 框架")

print(f"\n🚀 下一步:")
print(f"   1. 集成到抽取脚本 (exact_deepseek.py)")
print(f"   2. 在 Prompt 中注入检索到的模式")
print(f"   3. 对比有/无 RAG 的抽取质量")

print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
