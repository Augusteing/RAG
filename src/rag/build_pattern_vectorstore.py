# -*- coding: utf-8 -*-
"""
构建依存路径模式的向量数据库
使用 BGE-large-zh-v1.5 + ChromaDB
"""
import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

import torch
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 80)
print("🔧 PHM 依存路径模式向量数据库构建工具")
print("=" * 80)

# ==================== 配置部分 ====================

# 路径配置
CSV_FILE = PROJECT_ROOT / "data" / "processed" / "dependency_patterns" / "semantic_syntactic_patterns_report_2025-10-14_172830.csv"
CHROMA_DB_DIR = PROJECT_ROOT / "data" / "vectorstores" / "pattern_chroma_db"
COLLECTION_NAME = "phm_dependency_patterns"

# 模型配置
EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"
BATCH_SIZE = 32  # 批量编码大小（根据显存调整）

# 小规模测试模式（可通过环境变量控制）
TEST_MODE = os.getenv("TEST_MODE", "0") == "1"
TEST_SAMPLE_SIZE = 20  # 测试时只处理前 N 条

# ==================== 工具函数 ====================

def check_gpu():
    """检查 GPU 可用性"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ 检测到 GPU: {gpu_name} ({gpu_memory:.2f} GB)")
        return True
    else:
        print("⚠️ 未检测到 GPU，将使用 CPU（速度较慢）")
        return False

def load_patterns_from_csv(csv_path: Path) -> pd.DataFrame:
    """从 CSV 加载依存路径模式"""
    print(f"\n📂 加载依存路径模式: {csv_path}")
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 文件不存在: {csv_path}")
    
    # 读取 CSV（假设列名为: 语义模式, 总频次, 句法实现路径）
    df = pd.read_csv(csv_path)
    
    print(f"✅ 加载成功: {len(df)} 条模式")
    print(f"   列名: {list(df.columns)}")
    
    # 标准化列名（兼容带/不带英文注释的列名）
    column_mapping = {}
    for col in df.columns:
        if "语义模式" in col:
            column_mapping[col] = "语义模式"
        elif "总频次" in col or "频次" in col:
            column_mapping[col] = "总频次"
        elif "句法" in col and "路径" in col:
            column_mapping[col] = "句法实现路径"
    
    df = df.rename(columns=column_mapping)
    print(f"   标准化后列名: {list(df.columns)}")
    
    # 检查必要列
    required_cols = ["语义模式", "总频次", "句法实现路径"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"CSV 缺少必要列: {missing}，当前列: {list(df.columns)}")
    
    return df

def prepare_documents(df: pd.DataFrame, test_mode: bool = False) -> List[Dict[str, Any]]:
    """准备文档列表（用于向量化和存储）"""
    print(f"\n📝 准备文档...")
    
    if test_mode:
        df = df.head(TEST_SAMPLE_SIZE)
        print(f"⚠️ 测试模式：仅处理前 {TEST_SAMPLE_SIZE} 条")
    
    documents = []
    for idx, row in df.iterrows():
        # 构建文档内容（用于向量化）
        # 策略：结合语义模式和句法路径，提供更丰富的语义信息
        content = f"{row['语义模式']} | 句法路径: {row['句法实现路径']}"
        
        # 元数据（用于检索后的信息展示）
        metadata = {
            "pattern_id": str(idx),
            "semantic_pattern": row['语义模式'],
            "syntactic_path": row['句法实现路径'],
            "frequency": int(row['总频次']),
            "created_at": datetime.now().isoformat()
        }
        
        documents.append({
            "id": f"pattern_{idx}",
            "content": content,
            "metadata": metadata
        })
    
    print(f"✅ 准备完成: {len(documents)} 个文档")
    return documents

def create_embeddings(documents: List[Dict[str, Any]], model: SentenceTransformer, batch_size: int = 32):
    """批量生成 embeddings"""
    print(f"\n🔄 生成向量表示...")
    print(f"   - 批量大小: {batch_size}")
    print(f"   - 文档数量: {len(documents)}")
    
    contents = [doc["content"] for doc in documents]
    
    # 批量编码（显示进度条）
    embeddings = model.encode(
        contents,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print(f"✅ 向量生成完成")
    print(f"   - 向量维度: {embeddings.shape[1]}")
    print(f"   - 向量数量: {embeddings.shape[0]}")
    
    if torch.cuda.is_available():
        print(f"   - GPU 显存峰值: {torch.cuda.max_memory_allocated(0) / 1024**3:.2f} GB")
    
    return embeddings

def build_chromadb(documents: List[Dict[str, Any]], embeddings, db_dir: Path, collection_name: str):
    """构建 ChromaDB 向量数据库"""
    print(f"\n💾 构建 ChromaDB 向量数据库...")
    print(f"   - 存储路径: {db_dir}")
    print(f"   - Collection: {collection_name}")
    
    # 确保目录存在
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化 ChromaDB 客户端
    client = chromadb.PersistentClient(
        path=str(db_dir),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    # 删除旧 collection（如果存在）
    try:
        client.delete_collection(name=collection_name)
        print("   ℹ️ 已删除旧 collection")
    except Exception:
        pass
    
    # 创建新 collection
    collection = client.create_collection(
        name=collection_name,
        metadata={
            "description": "PHM 依存路径模式向量库",
            "embedding_model": EMBEDDING_MODEL,
            "created_at": datetime.now().isoformat()
        }
    )
    
    # 添加文档和向量
    collection.add(
        ids=[doc["id"] for doc in documents],
        embeddings=embeddings.tolist(),
        documents=[doc["content"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents]
    )
    
    print(f"✅ 向量数据库构建完成")
    print(f"   - 总条目数: {collection.count()}")
    
    return collection

def test_retrieval(collection, model: SentenceTransformer):
    """测试检索功能"""
    print(f"\n🔍 测试检索功能...")
    
    # 测试查询
    test_queries = [
        "深度学习模型预测设备故障",
        "传感器数据用于健康监测",
        "算法提升诊断准确率"
    ]
    
    for query in test_queries:
        print(f"\n   查询: {query}")
        
        # 生成查询向量
        query_embedding = model.encode([query], convert_to_numpy=True)
        
        # 检索 Top 3
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=3
        )
        
        print(f"   Top 3 相似模式:")
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"      {i}. [{meta['semantic_pattern']}] (距离: {dist:.3f})")
            print(f"         频次: {meta['frequency']}, 句法: {meta['syntactic_path']}")

# ==================== 主流程 ====================

def main():
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查 GPU
    has_gpu = check_gpu()
    
    # 2. 加载模型
    print(f"\n📥 加载 Embedding 模型: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    if has_gpu:
        model = model.to('cuda')
        print(f"✅ 模型已加载到 GPU")
    else:
        print(f"✅ 模型已加载到 CPU")
    
    # 3. 加载 CSV 数据
    df = load_patterns_from_csv(CSV_FILE)
    
    # 4. 准备文档
    documents = prepare_documents(df, test_mode=TEST_MODE)
    
    # 5. 生成 embeddings
    embeddings = create_embeddings(documents, model, batch_size=BATCH_SIZE)
    
    # 6. 构建 ChromaDB
    collection = build_chromadb(documents, embeddings, CHROMA_DB_DIR, COLLECTION_NAME)
    
    # 7. 测试检索
    test_retrieval(collection, model)
    
    print("\n" + "=" * 80)
    print("✅ 向量数据库构建完成！")
    print("=" * 80)
    print(f"📊 统计信息:")
    print(f"   - 模式总数: {len(documents)}")
    print(f"   - 向量维度: {embeddings.shape[1]}")
    print(f"   - 存储路径: {CHROMA_DB_DIR}")
    print(f"   - Collection: {COLLECTION_NAME}")
    print(f"\n💡 使用方法:")
    print(f"   从其他脚本加载:")
    print(f"   ```python")
    print(f"   import chromadb")
    print(f"   client = chromadb.PersistentClient(path='{CHROMA_DB_DIR}')")
    print(f"   collection = client.get_collection('{COLLECTION_NAME}')")
    print(f"   ```")
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
