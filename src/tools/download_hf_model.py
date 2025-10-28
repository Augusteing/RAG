# -*- coding: utf-8 -*-
"""
简单的 Hugging Face 模型下载工具
- 目标：将仓库完整下载到本地目录，供 local_files_only 加载
- 支持设置镜像（通过 HF_ENDPOINT / HUGGINGFACE_HUB_ENDPOINT 环境变量）

用法（PowerShell）：
  python src/tools/download_hf_model.py --repo BAAI/bge-large-zh-v1.5 --dest "E:/langchain/configs/models/bge-large-zh-v1.5"
可选：
  $env:HF_ENDPOINT = "https://hf-mirror.com"
"""
import argparse
import os
from pathlib import Path
from huggingface_hub import snapshot_download


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="HF 仓库名，如 BAAI/bge-large-zh-v1.5")
    parser.add_argument("--dest", required=True, help="下载目标目录，如 E:/langchain/configs/models/bge-large-zh-v1.5")
    parser.add_argument("--revision", default=None, help="可选：指定 revision/tag/commit")
    args = parser.parse_args()

    repo_id = args.repo
    dest_dir = Path(args.dest)
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"📦 下载模型: {repo_id}")
    print(f"📁 目标目录: {dest_dir}")
    if os.getenv("HF_ENDPOINT") or os.getenv("HUGGINGFACE_HUB_ENDPOINT"):
        print(f"🌐 使用镜像: {os.getenv('HF_ENDPOINT') or os.getenv('HUGGINGFACE_HUB_ENDPOINT')}")
    else:
        print("ℹ️ 未设置镜像，将直接从 huggingface.co 下载（可能较慢或受限）")

    # 将 snapshot 下载到缓存，再复制到目标目录（local_dir 参数直接输出）
    snapshot_download(
        repo_id=repo_id,
        local_dir=str(dest_dir),
        local_dir_use_symlinks=False,
        revision=args.revision,
        # allow_patterns=None,  # 如需精简可指定
        # ignore_patterns=None,
    )

    print("✅ 下载完成！")


if __name__ == "__main__":
    main()
