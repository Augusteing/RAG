# -*- coding: utf-8 -*-
"""环境诊断脚本"""
import sys
import os
from pathlib import Path

print("=" * 80)
print("🔍 PHM 知识图谱项目 - 环境诊断报告")
print("=" * 80)

# 1. Python 环境
print("\n【1】Python 环境")
print(f"   Python 版本: {sys.version.split()[0]}")
print(f"   Python 路径: {sys.executable}")
print(f"   Conda 环境: {os.getenv('CONDA_DEFAULT_ENV', 'N/A')}")

# 2. 硬件信息
print("\n【2】硬件配置")
try:
    import torch
    print(f"   ✅ PyTorch: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"   ✅ CUDA 可用: {torch.version.cuda}")
        print(f"   ✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"   ✅ 显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print(f"   ⚠️ CUDA 不可用（使用 CPU 模式）")
except Exception as e:
    print(f"   ❌ PyTorch 未安装或有问题: {e}")

# 3. RAG 核心库
print("\n【3】RAG 核心库")
try:
    import langchain
    print(f"   ✅ LangChain: {langchain.__version__}")
except Exception as e:
    print(f"   ❌ LangChain: {e}")

try:
    import chromadb
    print(f"   ✅ ChromaDB: {chromadb.__version__}")
except Exception as e:
    print(f"   ❌ ChromaDB: {e}")

try:
    import sentence_transformers
    print(f"   ✅ Sentence-Transformers: {sentence_transformers.__version__}")
except Exception as e:
    print(f"   ❌ Sentence-Transformers: {e}")

try:
    import pandas
    print(f"   ✅ Pandas: {pandas.__version__}")
except Exception as e:
    print(f"   ❌ Pandas: {e}")

# 4. LLM API 库
print("\n【4】LLM API 库")
try:
    import openai
    print(f"   ✅ OpenAI SDK: {openai.__version__}")
except Exception as e:
    print(f"   ❌ OpenAI SDK: {e}")

# 5. 环境变量检查
print("\n【5】API 密钥配置")
api_keys = {
    "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
    "KIMI_API_KEY": os.getenv("KIMI_API_KEY"),
    "MOONSHOT_API_KEY": os.getenv("MOONSHOT_API_KEY"),
    "HIAPI_API_KEY": os.getenv("HIAPI_API_KEY"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
}

for key_name, key_value in api_keys.items():
    if key_value:
        masked = f"{key_value[:6]}...{key_value[-4:]}" if len(key_value) > 10 else "***"
        print(f"   ✅ {key_name}: {masked}")
    else:
        print(f"   ⚠️ {key_name}: 未配置")

# 6. 项目结构检查
print("\n【6】项目结构")
project_root = Path(__file__).parent.parent
important_paths = {
    "论文数据": project_root / "data" / "raw" / "papers",
    "依存模式CSV": project_root / "data" / "processed" / "dependency_patterns" / "semantic_syntactic_patterns_report_2025-10-14_172830.csv",
    "Schema文件": project_root / "schema" / "phm_semantic_patterns.json",
    "向量数据库": project_root / "data" / "vectorstores" / "pattern_chroma_db",
    "抽取脚本": project_root / "src" / "extraction" / "extractors",
    "RAG脚本": project_root / "src" / "rag",
}

for name, path in important_paths.items():
    if path.exists():
        if path.is_dir():
            try:
                count = len(list(path.iterdir()))
                print(f"   ✅ {name}: {path} ({count} 项)")
            except:
                print(f"   ✅ {name}: {path}")
        else:
            size = path.stat().st_size / 1024
            print(f"   ✅ {name}: {path} ({size:.1f} KB)")
    else:
        print(f"   ⚠️ {name}: {path} (不存在)")

# 7. 性能测试
print("\n【7】快速性能测试")
try:
    import torch
    import time
    if torch.cuda.is_available():
        # GPU 测试
        print(f"   测试 GPU 计算...")
        x = torch.randn(1000, 1000, device='cuda')
        start = time.time()
        y = torch.matmul(x, x)
        torch.cuda.synchronize()
        elapsed = time.time() - start
        print(f"   ✅ GPU 矩阵运算 (1000x1000): {elapsed*1000:.2f} ms")
        print(f"   ✅ GPU 显存占用: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
    else:
        print(f"   ⚠️ GPU 不可用，跳过测试")
except Exception as e:
    print(f"   ❌ 性能测试失败: {e}")

# 8. 建议
print("\n" + "=" * 80)
print("💡 环境评估与建议")
print("=" * 80)

issues = []
suggestions = []

# 检查问题
try:
    import torch
    if not torch.cuda.is_available():
        issues.append("GPU 不可用")
        suggestions.append("重新安装 CUDA 版本的 PyTorch")
except:
    issues.append("PyTorch 未安装")
    suggestions.append("安装 PyTorch: pip install torch --index-url https://download.pytorch.org/whl/cu118")

if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENAI_API_KEY"):
    issues.append("缺少主要 API 密钥")
    suggestions.append("配置至少一个 LLM API 密钥（DEEPSEEK_API_KEY 或 OPENAI_API_KEY）")

vector_db = project_root / "data" / "vectorstores" / "pattern_chroma_db"
if not vector_db.exists():
    issues.append("向量数据库未构建")
    suggestions.append("运行: python src/rag/build_pattern_vectorstore.py")

if issues:
    print("\n⚠️ 发现的问题:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    
    print("\n💡 建议的修复措施:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
else:
    print("\n✅ 环境配置完美！所有组件就绪。")
    print("\n🚀 可以开始 RAG 测试:")
    print("   1. 构建向量数据库: python src/rag/build_pattern_vectorstore.py")
    print("   2. 测试 RAG 检索: python src/rag/test_retrieval.py")
    print("   3. 集成到抽取流程: 修改 exact_*.py 脚本")

print("\n" + "=" * 80)
