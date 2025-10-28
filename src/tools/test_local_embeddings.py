# -*- coding: utf-8 -*-
from pathlib import Path
import os

# 优先使用新包
try:
    from langchain_huggingface import HuggingFaceEmbeddings as HFEmbeddings
    impl = "langchain_huggingface"
except Exception:
    from langchain_community.embeddings import HuggingFaceEmbeddings as HFEmbeddings
    impl = "langchain_community"

MODEL_DIR = Path(r"E:\\langchain\\configs\\models\\bge-large-zh-v1.5")

print("Implementation:", impl)
print("Model dir:", MODEL_DIR)

if not MODEL_DIR.exists():
    raise SystemExit(f"模型目录不存在: {MODEL_DIR}")

emb = HFEmbeddings(
    model_name=str(MODEL_DIR),
    model_kwargs={"local_files_only": True, "device": os.getenv("EMBEDDING_DEVICE", "cpu")},
    encode_kwargs={"normalize_embeddings": True},
)

v = emb.embed_query("测试向量")
print("OK vector dim:", len(v))
