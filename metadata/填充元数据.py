import re
import json
import argparse
import csv
from pathlib import Path
from typing import List, Optional, Dict, Tuple

# ------------------ 配置 ------------------
DEFAULT_METADATA_FILE = Path(r"E:\知识图谱构建\文献信息\PHM-217篇摘要.txt")
TARGET_MODELS = ["deepseek", "gemini", "kimi"]  # 需要填充的抽取模型


# ------------------ 元数据解析 ------------------
RE_TITLE = re.compile(r"(?m)^Title-题名:\s*(.+)")
RE_AUTHOR = re.compile(r"(?m)^Author-作者:\s*(.+)")
RE_ORGAN = re.compile(r"(?m)^Organ-机构:\s*(.+)")
RE_PUB = re.compile(r"(?m)^PubTime-出版时间:\s*(.+)")

RE_RECORD = re.compile(r"(?m)^Title-题名:.*?(?=^Title-题名:|\Z)", re.DOTALL)


def _split_items(s: str) -> List[str]:
    parts = re.split(r"[;；、，,]+", s)
    items = [p.strip() for p in parts if p and p.strip()]
    items = [re.sub(r"^[\-—·•]\s*", "", it) for it in items]
    return items


def parse_metadata_file(path: Path) -> List[Dict[str, object]]:
    """解析聚合元数据文件，返回每篇的 dict。
    允许文件中包含 200+ 记录；通过 Title-题名 作为分隔。
    """
    if not path.exists():
        raise FileNotFoundError(f"元数据文件不存在: {path}")
    text = path.read_text(encoding="utf-8", errors="ignore")
    records = []
    for block in RE_RECORD.findall(text):
        title_m = RE_TITLE.search(block)
        if not title_m:
            continue
        title = title_m.group(1).strip()
        authors_m = RE_AUTHOR.search(block)
        orgs_m = RE_ORGAN.search(block)
        pub_m = RE_PUB.search(block)
        authors = _split_items(authors_m.group(1)) if authors_m else []
        orgs = _split_items(orgs_m.group(1)) if orgs_m else []
        pub_time = pub_m.group(1).strip() if pub_m else ""
        if title:
            records.append({
                "title": title,
                "authors": authors,
                "orgs": orgs,
                "pub_time": pub_time,
            })
    return records


def normalize_name(s: str) -> str:
    return re.sub(r"[\s_\-—:：,，；;·•.!！?？'""()（）\[\]【】]", "", s).lower()


def build_meta_index(metas: List[Dict[str, object]]):
    # 返回按 normalized title 长度降序的元组列表 (norm_title, meta)
    pairs = []
    for m in metas:
        t = str(m.get("title", ""))
        if not t:
            continue
        pairs.append((normalize_name(t), m))
    # 更长的标题优先匹配
    pairs.sort(key=lambda x: len(x[0]), reverse=True)
    return pairs


def find_meta_for_stem(stem: str, indexed_metas: List[Tuple[str, Dict[str, object]]]) -> Optional[Dict[str, object]]:
    norm_stem = normalize_name(stem)
    for norm_title, meta in indexed_metas:
        if norm_stem.startswith(norm_title):
            return meta
    return None


def dedup_entities(entities: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen: set[Tuple[str, str]] = set()
    result: List[Dict[str, str]] = []
    for e in entities:
        t = e.get("text", "").strip()
        ty = e.get("type", "").strip()
        key = (t.lower(), ty)
        if key in seen:
            continue
        seen.add(key)
        result.append({"text": t, "type": ty})
    return result


# ------------------ 发表单位 规范化辅助 ------------------
ORG_CITY_POSTCODE_PATTERN = re.compile(r"(西安|陕西西安)\s*\d{6}")

def canonical_org(text: str) -> str:
        """将机构变体统一到用于判重的 canonical 形式.
        规则:
            1) 去除常见城市+邮编片段: (西安|陕西西安) + 6位数字
            2) 去掉所有空白与常见标点
            3) 全部转小写
        这样: '西北工业大学航空学院 西安710072' 与 '西北工业大学航空学院' 视为同一。
        """
        s = ORG_CITY_POSTCODE_PATTERN.sub('', text)
        s = re.sub(r"[，,。;；:：()（）\s]", "", s)
        return s.lower()


def dedup_relations(relations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen: set[Tuple[str, str, str]] = set()
    result: List[Dict[str, str]] = []
    for r in relations:
        head = r.get("head", "").strip()
        tail = r.get("tail", "").strip()
        ty = r.get("type", "").strip()
        key = (head, tail, ty)
        if key in seen:
            continue
        seen.add(key)
        result.append({"head": head, "tail": tail, "type": ty})
    return result


def augment_one(json_path: Path, meta: Dict[str, object], dry_run: bool = False) -> Dict[str, object]:
    """将 meta 中元信息追加到指定 JSON；若候选实体/关系已存在则记录但不重复添加。

    返回结构:
      {
        'changed': bool,
        'added_entities': [...],
        'added_relations': [...],
        'duplicate_entities': [...],   # 已存在而未添加
        'duplicate_relations': [...]
      }
    """
    result = {
        'changed': False,
        'added_entities': [],
        'added_relations': [],
        'duplicate_entities': [],
        'duplicate_relations': []
    }
    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] 读取失败 {json_path.name}: {e}")
        return result

    if isinstance(raw, dict):
        item = raw
        container = raw
    elif isinstance(raw, list) and raw and isinstance(raw[0], dict):
        item = raw[0]
        container = raw
    else:
        print(f"[WARN] 不支持的结构: {json_path}")
        return result

    entities = item.get("entities") or []
    relations = item.get("relations") or []
    if not isinstance(entities, list) or not isinstance(relations, list):
        print(f"[WARN] entities/relations 非列表: {json_path}")
        return result

    title: str = str(meta.get("title", ""))
    authors: List[str] = meta.get("authors", [])  # type: ignore
    orgs: List[str] = meta.get("orgs", [])  # type: ignore
    pub_time: str = str(meta.get("pub_time", ""))

    candidate_entities: List[Dict[str, str]] = []
    if title:
        candidate_entities.append({"type": "论文", "text": title})
    for a in authors:
        if a:
            candidate_entities.append({"type": "作者", "text": a})
    for o in orgs:
        if o:
            candidate_entities.append({"type": "发表单位", "text": o})
    if pub_time:
        candidate_entities.append({"type": "发表时间", "text": pub_time})

    candidate_relations: List[Dict[str, str]] = []
    for a in authors:
        if a and title:
            candidate_relations.append({"type": "撰写", "head": a, "tail": title})
    if authors and orgs and authors[0] and orgs[0]:
        candidate_relations.append({"type": "隶属", "head": authors[0], "tail": orgs[0]})
    if title and pub_time:
        candidate_relations.append({"type": "发表于", "head": title, "tail": pub_time})

    existing_entity_keys = {(e.get('text','').strip().lower(), e.get('type','').strip()) for e in entities}
    # 单独维护发表单位的 canonical key 集合
    existing_org_canon = {canonical_org(e.get('text','')) for e in entities if e.get('type') == '发表单位'}
    existing_rel_keys = {(r.get('head','').strip(), r.get('tail','').strip(), r.get('type','').strip()) for r in relations}

    new_entities = []
    for ce in candidate_entities:
        raw_text = ce.get('text','').strip()
        etype = ce.get('type','').strip()
        key = (raw_text.lower(), etype)
        is_duplicate = False
        if etype == '发表单位':
            canon = canonical_org(raw_text)
            if canon in existing_org_canon:
                is_duplicate = True
            else:
                existing_org_canon.add(canon)
        if not is_duplicate and key not in existing_entity_keys:
            new_entities.append(ce)
            existing_entity_keys.add(key)
            result['added_entities'].append(ce)
        else:
            result['duplicate_entities'].append(ce)

    new_relations = []
    for cr in candidate_relations:
        key = (cr.get('head','').strip(), cr.get('tail','').strip(), cr.get('type','').strip())
        if key in existing_rel_keys:
            result['duplicate_relations'].append(cr)
        else:
            new_relations.append(cr)
            existing_rel_keys.add(key)
            result['added_relations'].append(cr)

    if new_entities or new_relations:
        result['changed'] = True
        if not dry_run:
            # 仍然使用去重函数保证整体唯一性
            item['entities'] = dedup_entities(entities + new_entities)
            item['relations'] = dedup_relations(relations + new_relations)
            try:
                json_path.write_text(json.dumps(container, ensure_ascii=False, indent=2), encoding='utf-8')
            except Exception as e:
                print(f"[ERROR] 写回失败 {json_path.name}: {e}")
    return result


def main():
    parser = argparse.ArgumentParser(description="将聚合元数据填充到各模型 in_scope JSON")
    parser.add_argument("--metadata-file", default=str(DEFAULT_METADATA_FILE), help="聚合元数据 txt 路径")
    parser.add_argument("--models", default=",".join(TARGET_MODELS), help="需要处理的模型列表，逗号分隔")
    parser.add_argument("--dry-run", action="store_true", help="不写入，仅统计将发生的修改数")
    parser.add_argument("--limit", type=int, default=0, help="每模型最多处理 JSON 数 (0=不限)")
    parser.add_argument("--existing-report", type=str, default=None, help="记录已存在(重复)的元数据项 CSV 路径")
    args = parser.parse_args()

    meta_file = Path(args.metadata_file)
    models = [m.strip() for m in args.models.split(',') if m.strip()]
    if not models:
        print("[ERROR] 未提供模型名称")
        return

    # 自动向上查找包含 '数据结果' 的抽取根目录，避免层级硬编码错误
    script_dir = Path(__file__).resolve().parent
    extract_root = None
    for p in [script_dir] + list(script_dir.parents):
        if (p / '数据结果').is_dir():
            extract_root = p
            break
    if extract_root is None:
        print('[ERROR] 未能找到包含 数据结果 的目录，请确认结构或显式提供 --metadata-file。')
        return
    data_base = extract_root / "数据结果"

    print(f"[信息] 元数据文件: {meta_file}")
    metas = parse_metadata_file(meta_file)
    print(f"[信息] 解析得到元数据记录: {len(metas)} 条")
    if not metas:
        print("[ERROR] 没有解析到任何记录，退出。")
        return
    indexed = build_meta_index(metas)

    total_updated = 0
    total_skipped_no_meta = 0
    total_unchanged = 0

    for model in models:
        json_dir = data_base / f"提取结果_by_{model}" / "in_scope"
        if not json_dir.exists():
            print(f"[警告] 模型 {model} 目录不存在: {json_dir}")
            continue
        json_files = sorted(json_dir.glob("*.json"))
        if args.limit > 0:
            json_files = json_files[: args.limit]
        print(f"[模型 {model}] 待处理 JSON 数: {len(json_files)} (目录: {json_dir})")

        m_updated = m_no_meta = m_unchanged = 0
        duplicate_rows = []  # model-level duplicates per file
        for jp in json_files:
            meta = find_meta_for_stem(jp.stem, indexed)
            if not meta:
                m_no_meta += 1
                continue
            res = augment_one(jp, meta, dry_run=args.dry_run)
            if res['changed']:
                m_updated += 1
            else:
                m_unchanged += 1
            # 记录重复项
            for e in res['duplicate_entities']:
                duplicate_rows.append(['entity', e.get('type',''), e.get('text','') , '', jp.name])
            for r in res['duplicate_relations']:
                duplicate_rows.append(['relation', r.get('type',''), r.get('head',''), r.get('tail',''), jp.name])

        # 写重复项报告（按模型追加）
        if duplicate_rows:
            if args.existing_report:
                report_path = Path(args.existing_report)
            else:
                report_path = data_base / '元数据填充_已存在项.csv'
            write_header = not report_path.exists()
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with report_path.open('a', newline='', encoding='utf-8-sig') as rf:
                w = csv.writer(rf)
                if write_header:
                    w.writerow(['model','file','kind','type','text_or_head','tail'])
                for kind, ty, text_or_head, tail, fname in duplicate_rows:
                    w.writerow([model, fname, kind, ty, text_or_head, tail])
            print(f"[模型 {model}] 记录已存在元数据 {len(duplicate_rows)} 条 -> {report_path}")

        total_updated += m_updated
        total_skipped_no_meta += m_no_meta
        total_unchanged += m_unchanged
        print(f"[模型 {model}] 新增/更新 {m_updated}，缺少元数据 {m_no_meta}，已存在/未变化 {m_unchanged}")

    mode = "DRY-RUN" if args.dry_run else "WRITE"
    print(f"[汇总 {mode}] 更新 {total_updated}，未匹配元数据 {total_skipped_no_meta}，未变化 {total_unchanged}")


if __name__ == "__main__":
    main()
