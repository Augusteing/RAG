import argparse
import json
import os
from pathlib import Path


def collect_files(input_dir: Path, exts=(".md", ".txt"), limit: int | None = None):
    files = []
    for ext in exts:
        files.extend(sorted(input_dir.rglob(f"*{ext}")))
    if limit is not None:
        files = files[:limit]
    return files


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="gb18030", errors="ignore")


def build_tasks_text(input_dir: Path, limit: int | None = None):
    tasks = []
    for f in collect_files(input_dir, limit=limit):
        content = read_text(f)
        tasks.append({
            "data": {
                "text": content,
                "file_path": str(f),
                "doc_id": f.stem,
                "source": "local",
            }
        })
    return tasks


def main():
    parser = argparse.ArgumentParser(description="Prepare Label Studio tasks from text/markdown files.")
    parser.add_argument("--input", type=str, default="data/raw/papers/test", help="Input directory containing .md/.txt files")
    parser.add_argument("--output", type=str, default="label_studio_tasks.json", help="Output JSON file path")
    parser.add_argument("--limit", type=int, default=20, help="Max number of files to include")
    args = parser.parse_args()

    input_dir = Path(args.input)
    assert input_dir.exists(), f"Input directory not found: {input_dir}"

    tasks = build_tasks_text(input_dir, limit=args.limit)
    out_path = Path(args.output)
    out_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(tasks)} tasks to {out_path}")


if __name__ == "__main__":
    main()