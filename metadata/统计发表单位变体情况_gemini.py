import json
import re
from pathlib import Path
import csv
from typing import Dict, List, Set

"""
统计增补后 GEMINI 抽取结果中 '发表单位' 实体的“同一机构多变体”情况。

判定标准:
  对同一 JSON 文件中, 所有 type == '发表单位' 的实体取去重文本集合 T。
  使用 canonical_org(text) 归一化后若某个 canonical 拥有 >1 不同原始文本, 记为一例“变体冲突”。

输出:
  1) 控制台汇总
  2) CSV: 统计/发表单位变体_gemini.csv (每行一个文件的一个 canonical 冲突)
     列: file, canonical, variant_count, variants(以 | 分隔)
  3) CSV: 统计/发表单位变体汇总_gemini.csv (聚合级别) 列: canonical, files_involved, total_variant_sets

注意: 仅分析 增补后-EXP2/提取结果_by_gemini/in_scope
"""

SCRIPT_DIR = Path(__file__).resolve().parent

# 自动向上找到包含 '数据结果/增补后-EXP2/提取结果_by_gemini/in_scope'
def locate_gemini_augmented(start: Path) -> Path:
    for p in [start, *start.parents]:
        target = p / '数据结果' / '增补后-EXP2' / '提取结果_by_gemini' / 'in_scope'
        if target.exists():
            return target
    return start / '数据结果' / '增补后-EXP2' / '提取结果_by_gemini' / 'in_scope'


ORG_CITY_POSTCODE_PATTERN = re.compile(r"(西安|陕西西安)\s*\d{6}")

def canonical_org(text: str) -> str:
    s = ORG_CITY_POSTCODE_PATTERN.sub('', text)
    s = re.sub(r"[，,。;；:：()（）\s]", "", s)
    return s.lower()


def main():
    in_scope = locate_gemini_augmented(SCRIPT_DIR)
    if not in_scope.exists():
        print(f"[ERROR] 未找到 gemini 增补后目录: {in_scope}")
        return
    files = sorted(in_scope.glob('*.json'))
    total_files = len(files)
    conflict_records = []  # per-file per-canonical
    canonical_file_map: Dict[str, Set[str]] = {}
    conflict_count_files = 0

    for jp in files:
        try:
            data = json.loads(jp.read_text(encoding='utf-8'))
        except Exception:
            continue
        if isinstance(data, dict):
            entities = data.get('entities') or []
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            entities = data[0].get('entities') or []
        else:
            continue
        # 收集发表单位文本去重
        org_texts = {e.get('text','').strip() for e in entities if e.get('type') == '发表单位' and e.get('text')}
        if not org_texts:
            continue
        # 分组
        canon_map: Dict[str, List[str]] = {}
        for t in org_texts:
            c = canonical_org(t)
            canon_map.setdefault(c, []).append(t)
        file_has_conflict = False
        for c, variants in canon_map.items():
            if len(variants) > 1:
                file_has_conflict = True
                conflict_records.append([
                    jp.name,
                    c,
                    len(variants),
                    ' | '.join(sorted(variants, key=len))
                ])
                canonical_file_map.setdefault(c, set()).add(jp.name)
        if file_has_conflict:
            conflict_count_files += 1

    stats_dir = in_scope.parent.parent / '统计'
    stats_dir.mkdir(parents=True, exist_ok=True)
    detail_csv = stats_dir / '发表单位变体_gemini.csv'
    summary_csv = stats_dir / '发表单位变体汇总_gemini.csv'

    # 写明细
    with detail_csv.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['file','canonical','variant_count','variants'])
        w.writerows(conflict_records)

    # 写汇总 (canonical 级别)
    with summary_csv.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['canonical','files_involved','file_count'])
        for c, fset in sorted(canonical_file_map.items(), key=lambda x: (-len(x[1]), x[0])):
            w.writerow([c, '|'.join(sorted(fset)), len(fset)])

    print('[统计完成]')
    print(f'  总文件数: {total_files}')
    print(f'  含发表单位变体冲突的文件数: {conflict_count_files}')
    print(f'  冲突记录条数(文件*canonical): {len(conflict_records)}')
    print(f'  明细 CSV: {detail_csv}')
    print(f'  汇总 CSV: {summary_csv}')


if __name__ == '__main__':
    main()
