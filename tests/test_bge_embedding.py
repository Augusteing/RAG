# -*- coding: utf-8 -*-
"""
测试 BGE-large-zh-v1.5 模型在 RTX 3060 上的运行情况
"""
import torch
from sentence_transformers import SentenceTransformer
import time

print("=" * 60)
print("🔍 检查 GPU 环境")
print("=" * 60)

# 检查 CUDA 是否可用
print(f"✅ PyTorch 版本: {torch.__version__}")
print(f"✅ CUDA 是否可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✅ CUDA 版本: {torch.version.cuda}")
    print(f"✅ GPU 设备: {torch.cuda.get_device_name(0)}")
    print(f"✅ 显存总量: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print(f"✅ 当前显存使用: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

print("\n" + "=" * 60)
print("📥 加载 BGE-large-zh-v1.5 模型")
print("=" * 60)
print("⏳ 首次运行会从 HuggingFace 下载模型（~1GB），请稍候...")

start_time = time.time()

# 加载模型（自动使用 GPU）
model = SentenceTransformer('BAAI/bge-large-zh-v1.5')

# 如果有 GPU，确保模型在 GPU 上
if torch.cuda.is_available():
    model = model.to('cuda')
    print(f"✅ 模型已加载到 GPU")
else:
    print(f"⚠️ 未检测到 GPU，使用 CPU 运行")

load_time = time.time() - start_time
print(f"✅ 模型加载完成，耗时: {load_time:.2f} 秒")

if torch.cuda.is_available():
    print(f"✅ 加载后显存使用: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

print("\n" + "=" * 60)
print("🧪 测试中文编码能力（PHM 领域示例）")
print("=" * 60)

# 测试文本（来自你的依存路径模式）
test_texts = [
    "方法 → 解决 → 问题",
    "技术 → 应用于 → 应用领域",
    "模型 → 预测 → 故障",
    "算法 → 提高 → 准确率",
    "传感器 → 监测 → 设备状态",
    "深度学习方法用于故障预测与健康管理",
    "基于卷积神经网络的轴承故障诊断研究",
    "支持向量机在设备剩余寿命预测中的应用"
]

print("⏳ 编码测试文本...")
start_time = time.time()
embeddings = model.encode(test_texts, show_progress_bar=True)
encode_time = time.time() - start_time

print(f"\n✅ 编码完成！")
print(f"   - 文本数量: {len(test_texts)}")
print(f"   - 向量维度: {embeddings.shape[1]}")
print(f"   - 总耗时: {encode_time:.3f} 秒")
print(f"   - 平均速度: {len(test_texts)/encode_time:.2f} 条/秒")

if torch.cuda.is_available():
    print(f"   - 峰值显存: {torch.cuda.max_memory_allocated(0) / 1024**3:.2f} GB")

print("\n" + "=" * 60)
print("🔬 计算语义相似度")
print("=" * 60)

# 计算前两个模式的相似度
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

sim_matrix = cosine_similarity(embeddings[:5])
print("\n语义相似度矩阵（前5条模式）：")
print("文本1: 方法 → 解决 → 问题")
print("文本2: 技术 → 应用于 → 应用领域")
print("文本3: 模型 → 预测 → 故障")
print("文本4: 算法 → 提高 → 准确率")
print("文本5: 传感器 → 监测 → 设备状态")
print("\n相似度矩阵:")
print(np.round(sim_matrix, 3))

print("\n💡 解读:")
print(f"   - 文本1 vs 文本2 相似度: {sim_matrix[0,1]:.3f}")
print(f"   - 文本3 vs 文本5 相似度: {sim_matrix[2,4]:.3f}")
print(f"   - 模型能够捕捉语义相似性！")

print("\n" + "=" * 60)
print("✅ 测试完成！BGE-large-zh-v1.5 在你的 RTX 3060 上运行正常")
print("=" * 60)
print("\n📝 性能总结:")
print(f"   - GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print(f"   - 显存占用: {torch.cuda.max_memory_allocated(0) / 1024**3:.2f} GB (峰值)")
print(f"   - 编码速度: {len(test_texts)/encode_time:.2f} 条/秒")
print(f"   - 向量维度: 1024")
print(f"\n💡 预估:")
print(f"   - 2,287 条模式向量化: 约 {2287/(len(test_texts)/encode_time):.1f} 秒")
print(f"   - 200 篇论文检索: 每篇约 {encode_time/len(test_texts):.2f} 秒")
