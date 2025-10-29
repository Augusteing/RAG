import argparse
import re
from pathlib import Path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="gb18030", errors="ignore")


CH_ABSTRACT_PATTERNS = [
    re.compile(r"^\s*[【\[]?摘[\s　]*要[】\]]?\s*[:：]?.*$"),
    re.compile(r"^\s*中文摘要\s*[:：]?.*$"),
]

EN_ABSTRACT_START = re.compile(r"^\s*(Abstract|ABSTRACT|Summary)\b.*")
EN_KEYWORDS_START = re.compile(r"^\s*(Keywords|KEYWORDS|Key\s*words|Index\s*Terms)\s*[:：].*")

CH_SECTION_PATTERNS = [
    re.compile(r"^\s*关键词\s*[:：].*$"),
    re.compile(r"^\s*(引言|绪论|前言|结论|参考文献|致谢)\b.*$"),
    re.compile(r"^\s*[一二三四五六七八九十]+[、\.．]\s*.*$"),
    re.compile(r"^\s*\d+(?:\.\d+)*\s+.*$"),
]


def find_chinese_abstract_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        for pat in CH_ABSTRACT_PATTERNS:
            if pat.match(line):
                return i
    return 0


def is_chinese_section(line: str) -> bool:
    for pat in CH_SECTION_PATTERNS:
        if pat.match(line):
            return True
    # Heuristic: line contains a significant amount of CJK characters
    cjk_count = sum(1 for ch in line if "\u4e00" <= ch <= "\u9fff")
    return cjk_count >= max(5, len(line) // 5)


def clean_lines(lines: list[str]) -> list[str]:
    # 1) Cut everything before first Chinese "摘要" header
    start_idx = find_chinese_abstract_start(lines)
    lines = lines[start_idx:]

    cleaned: list[str] = []
    in_en_abstract = False
    in_en_keywords = False

    for line in lines:
        if in_en_abstract:
            # End English abstract when we hit a Chinese section or blank line followed by Chinese
            if is_chinese_section(line) or line.strip() == "":
                in_en_abstract = False
                # If current line is meaningful Chinese section, keep it
                if is_chinese_section(line):
                    cleaned.append(line)
            # Else skip English abstract content
            continue

        if in_en_keywords:
            # End English keywords at blank line or Chinese section
            if line.strip() == "" or is_chinese_section(line):
                in_en_keywords = False
                if is_chinese_section(line):
                    cleaned.append(line)
            continue

        # Enter English abstract block
        if EN_ABSTRACT_START.match(line):
            in_en_abstract = True
            continue

        # Enter English keywords block
        if EN_KEYWORDS_START.match(line):
            in_en_keywords = True
            continue

        cleaned.append(line)

    # Remove leading blank lines after cutting
    while cleaned and cleaned[0].strip() == "":
        cleaned.pop(0)
    return cleaned


def process_file(inp: Path, out: Path):
    text = read_text(inp)
    lines = text.splitlines()
    cleaned_lines = clean_lines(lines)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(cleaned_lines), encoding="utf-8")


def collect_files(category_dir: Path, exts=(".md", ".txt")) -> list[Path]:
    files: list[Path] = []
    for ext in exts:
        files.extend(sorted(category_dir.glob(f"*{ext}")))
    return files


def main():
    parser = argparse.ArgumentParser(description="Clean PHM paper markdown/txt: cut before '摘要', remove English Abstract & Keywords.")
    parser.add_argument("--input-root", type=str, default="data/raw/papers", help="Input root containing category subfolders")
    parser.add_argument("--output-root", type=str, default="data/processed/papers", help="Output root for cleaned files")
    parser.add_argument("--categories", type=str, default="auto", help="Comma-separated categories (default: auto discover)")
    args = parser.parse_args()

    input_root = Path(args.input_root)
    output_root = Path(args.output_root)
    assert input_root.exists(), f"Input root not found: {input_root}"

    if args.categories == "auto":
        categories = [p.name for p in input_root.iterdir() if p.is_dir()]
    else:
        categories = [c.strip() for c in args.categories.split(",") if c.strip()]

    processed_count = 0
    for cat in categories:
        in_cat = input_root / cat
        if not in_cat.exists() or not in_cat.is_dir():
            print(f"[skip] category not found: {in_cat}")
            continue
        out_cat = output_root / cat
        out_cat.mkdir(parents=True, exist_ok=True)

        for f in collect_files(in_cat):
            out_f = out_cat / f.name
            process_file(f, out_f)
            processed_count += 1
            print(f"[ok] {f} -> {out_f}")

    print(f"Done. Cleaned files: {processed_count}")


if __name__ == "__main__":
    main()