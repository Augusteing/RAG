# -*- coding: utf-8 -*-
"""
一致性分析脚本

输入目录（固定约定）：
  E:/langchain/outputs/extractions/consistency/
  ├── 1/
  │   ├── deepseek_rag/
  │   ├── gemini_rag/
  │   └── kimi_rag/
  ├── 2/
  │   ├── deepseek_rag/
  │   ├── gemini_rag/
  │   └── kimi_rag/
  └── 3/
      ├── deepseek_rag/
      └── gemini_rag/

输出目录（与其它分析脚本一致的极简风格）：
  E:/langchain/outputs/analysis/consistency/
  ├── consistency_summary.md
  ├── deepseek/paper_consistency.csv
  ├── gemini/paper_consistency.csv
  └── kimi/paper_consistency.csv

指标定义（基础版）：
  - 实体集合一致性（Jaccard 平均）：对同一论文跨多次运行的实体集合做成对 Jaccard 相似度，取平均
  - 关系集合一致性（Jaccard 平均）：同上
  - 规模稳定性（CV）：实体数、关系数在多次运行间的变异系数（std/mean）

实体键与关系键：
  - 实体键：normalize(name) + '::' + normalize(type)
  - 关系键：normalize(src_name+'::'+src_type) + '->' + normalize(relation_type) + '->' + normalize(tgt_name+'::'+tgt_type)

健壮性：
  - JSON 中键名可能不完全一致，做兼容提取；缺失则跳过。
  - 少于 2 次运行时，Jaccard/CV 记为 NA。
"""

from __future__ import annotations

import os
import json
import math
from pathlib import Path
from itertools import combinations
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any

import pandas as pd

CONSISTENCY_BASE = Path("E:/langchain/outputs/extractions/consistency")
OUTPUT_DIR = Path("E:/langchain/outputs/analysis/consistency")

MODEL_FOLDERS = {
    "deepseek": "deepseek_rag",
    "gemini": "gemini_rag",
    "kimi": "kimi_rag",
}


def norm_text(x: Any) -> str:
    if x is None:
        return ""
    s = str(x).strip().lower()
    # 可拓展：全角半角、特殊空格
    return " ".join(s.split())


def entity_key(ent: dict) -> str:
    name = ent.get("name") or ent.get("entity") or ent.get("text")
    etype = ent.get("type") or ent.get("entity_type") or ent.get("category")
    return f"{norm_text(name)}::{norm_text(etype)}"


def relation_key(rel: dict) -> str:
    # 兼容不同字段命名
    src_name = rel.get("source_name") or rel.get("source") or rel.get("from")
    src_type = rel.get("source_type") or rel.get("from_type") or rel.get("sourceEntityType")
    tgt_name = rel.get("target_name") or rel.get("target") or rel.get("to")
    tgt_type = rel.get("target_type") or rel.get("to_type") or rel.get("targetEntityType")
    rtype = rel.get("type") or rel.get("relation") or rel.get("relation_type")
    return f"{norm_text(src_name)}::{norm_text(src_type)}->{norm_text(rtype)}->{norm_text(tgt_name)}::{norm_text(tgt_type)}"


def load_json_safely(p: Path) -> dict | None:
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def extract_sets_from_file(p: Path) -> Tuple[Set[str], Set[str], int, int]:
    data = load_json_safely(p)
    if not isinstance(data, dict):
        return set(), set(), 0, 0
    ents = data.get("entities") or []
    rels = data.get("relations") or []
    ent_set = set()
    for e in ents:
        try:
            ent_set.add(entity_key(e))
        except Exception:
            continue
    rel_set = set()
    for r in rels:
        try:
            rel_set.add(relation_key(r))
        except Exception:
            continue
    return ent_set, rel_set, len(ents) if isinstance(ents, list) else 0, len(rels) if isinstance(rels, list) else 0


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    if union == 0:
        return 1.0
    return inter / union


def coeff_variation(values: List[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    if mean == 0:
        return None
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    std = math.sqrt(var)
    return std / mean


def scan_run_files(run_dir: Path, model_folder: str) -> Dict[str, Path]:
    """扫描单次运行中某模型的所有论文结果文件，返回 {paper_id: path}。
    paper_id 用文件名（去扩展名）。递归 rglob 以兼容子目录。
    """
    base = run_dir / model_folder
    results = {}
    if not base.exists():
        return results
    for p in base.rglob("*.json"):
        # 过滤掉明显的日志文件（名字包含 log）
        if "log" in p.name.lower():
            continue
        paper = p.stem
        results[paper] = p
    return results


def analyze_model(model_key: str, runs: List[Path]) -> pd.DataFrame:
    model_folder = MODEL_FOLDERS[model_key]

    # 收集每次运行的文件映射
    run_maps: List[Dict[str, Path]] = [scan_run_files(r, model_folder) for r in runs]

    # 汇总所有论文ID
    all_papers: Set[str] = set()
    for m in run_maps:
        all_papers.update(m.keys())

    rows = []
    for paper in sorted(all_papers):
        ent_sets: List[Set[str]] = []
        rel_sets: List[Set[str]] = []
        ent_counts: List[int] = []
        rel_counts: List[int] = []
        used_runs = 0

        for m in run_maps:
            path = m.get(paper)
            if not path:
                continue
            ent_set, rel_set, ec, rc = extract_sets_from_file(path)
            ent_sets.append(ent_set)
            rel_sets.append(rel_set)
            ent_counts.append(ec)
            rel_counts.append(rc)
            used_runs += 1

        # 计算平均 pairwise Jaccard
        def avg_pairwise_jacc(sets: List[Set[str]]) -> float | None:
            if len(sets) < 2:
                return None
            vals = []
            for a, b in combinations(sets, 2):
                vals.append(jaccard(a, b))
            return sum(vals) / len(vals) if vals else None

        ent_j = avg_pairwise_jacc(ent_sets)
        rel_j = avg_pairwise_jacc(rel_sets)
        ecv = coeff_variation(ent_counts)
        rcv = coeff_variation(rel_counts)

        rows.append({
            "paper": paper,
            "runs": used_runs,
            "entity_jaccard": None if ent_j is None else round(ent_j, 4),
            "relation_jaccard": None if rel_j is None else round(rel_j, 4),
            "entities_cv": None if ecv is None else round(ecv, 4),
            "relations_cv": None if rcv is None else round(rcv, 4),
            "avg_entities": round(sum(ent_counts) / used_runs, 2) if used_runs else None,
            "avg_relations": round(sum(rel_counts) / used_runs, 2) if used_runs else None,
        })

    return pd.DataFrame(rows)


def main():
    print("=" * 80)
    print("🔁 抽取结果一致性分析")
    print("=" * 80)

    # 收集有效的运行目录（数字命名）
    if not CONSISTENCY_BASE.exists():
        raise SystemExit(f"未找到目录: {CONSISTENCY_BASE}")

    runs = [d for d in CONSISTENCY_BASE.iterdir() if d.is_dir() and d.name.isdigit()]
    runs.sort(key=lambda p: int(p.name))
    print(f"发现运行次数: {len(runs)} -> {[p.name for p in runs]}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model_summaries = []
    for model_key in ["deepseek", "gemini", "kimi"]:
        df = analyze_model(model_key, runs)
        model_dir = OUTPUT_DIR / model_key
        model_dir.mkdir(parents=True, exist_ok=True)
        out_csv = model_dir / "paper_consistency.csv"
        df.to_csv(out_csv, index=False, encoding="utf-8-sig")
        print(f"   ✅ {model_key} 结果已保存: {out_csv}")

        # 统计汇总（忽略 NA）
        def safe_mean(series: pd.Series) -> float | None:
            s = series.dropna()
            return round(s.mean(), 4) if len(s) else None

        summary = {
            "模型": model_key,
            "论文数": len(df),
            "平均实体Jaccard": safe_mean(df["entity_jaccard"]) if not df.empty else None,
            "平均关系Jaccard": safe_mean(df["relation_jaccard"]) if not df.empty else None,
            "实体数CV(均值)": safe_mean(df["entities_cv"]) if not df.empty else None,
            "关系数CV(均值)": safe_mean(df["relations_cv"]) if not df.empty else None,
        }
        model_summaries.append(summary)

    # 生成汇总 Markdown
    md_file = OUTPUT_DIR / "consistency_summary.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# 抽取结果一致性分析报告\n\n")
        f.write(f"运行目录: `{CONSISTENCY_BASE}`\n\n")
        f.write(f"共发现 {len(runs)} 次运行: {', '.join(p.name for p in runs)}\n\n")

        if model_summaries:
            f.write("## 模型级汇总\n\n")
            headers = ["模型", "论文数", "平均实体Jaccard", "平均关系Jaccard", "实体数CV(均值)", "关系数CV(均值)"]
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
            for s in model_summaries:
                row = [
                    s["模型"],
                    s["论文数"],
                    s["平均实体Jaccard"],
                    s["平均关系Jaccard"],
                    s["实体数CV(均值)"],
                    s["关系数CV(均值)"],
                ]
                f.write("| " + " | ".join("" if v is None else str(v) for v in row) + " |\n")
            f.write("\n")

        f.write("## 文件结构\n\n")
        f.write("```)\n")
        f.write("outputs/analysis/consistency/\n")
        f.write("├── consistency_summary.md\n")
        f.write("├── deepseek/paper_consistency.csv\n")
        f.write("├── gemini/paper_consistency.csv\n")
        f.write("└── kimi/paper_consistency.csv\n")
        f.write("```)\n\n")

        f.write("## 指标说明\n\n")
        f.write("- 实体/关系 Jaccard: 跨运行的集合相似度（成对平均），越高越稳定\n")
        f.write("- 实体数/关系数 CV: 规模波动（std/mean），越低越稳定\n")
        f.write("- runs 列示该论文实际参与统计的运行次数（缺失会自动跳过）\n")

    print(f"\n✅ 汇总报告已保存: {md_file}")


if __name__ == "__main__":
    main()
