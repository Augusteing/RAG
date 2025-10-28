# -*- coding: utf-8 -*-
"""
RAG 增强版 DeepSeek 实体关系抽取脚本
使用 LangChain 检索相关模式作为 few-shot 示例
"""
import os
import json
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

# OpenAI SDK (用于 DeepSeek API)
from openai import OpenAI

# LangChain RAG 组件
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 进度条
from tqdm import tqdm

# ------------------------------
# 路径配置
# ------------------------------
CODE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CODE_DIR.parent.parent.parent

# Schema 文件
SCHEMA_FILE = PROJECT_ROOT / "configs" / "schemas" / "phm_semantic_patterns.json"

# Prompt 模板
PROMPT_FILE = PROJECT_ROOT / "configs" / "prompts" / "prompt.txt"  # 通用/回退模板（不修改）
EXP02_PROMPT_FILE = PROJECT_ROOT / "configs" / "prompts" / "exp02" / "prompt.txt"  # 仅实验二使用的新路径
EXP03_PROMPTS_DIR = PROJECT_ROOT / "configs" / "prompts" / "exp03"

# 论文目录
PAPERS_DIR = PROJECT_ROOT / "data" / "raw" / "papers"

# 向量数据库路径
VECTOR_DB_DIR = PROJECT_ROOT / "data" / "vectorstores" / "langchain_chroma_db"

# 实验选择：命令行优先，其次环境变量，默认 exp02
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument("--exp", dest="exp_id", choices=["exp02", "exp03"], default=None)
_parser.add_argument("--exp02", dest="exp02", action="store_true")
_parser.add_argument("--exp03", dest="exp03", action="store_true")
_parser.add_argument("--03", dest="exp03_short", action="store_true")
_parser.add_argument("--max", dest="max_papers", type=int, default=None)
_args, _unknown = _parser.parse_known_args()
_env_exp = os.getenv("EXP_ID")
if _args.exp_id in {"exp02", "exp03"}:
    EXP_ID = _args.exp_id
elif _args.exp03 or _args.exp03_short:
    EXP_ID = "exp03"
elif _args.exp02:
    EXP_ID = "exp02"
elif _env_exp in {"exp02", "exp03"}:
    EXP_ID = _env_exp
else:
    EXP_ID = "exp02"

# 限制处理篇数（可选）
MAX_PAPERS = _args.max_papers
if MAX_PAPERS is None:
    try:
        MAX_PAPERS = int(os.getenv("MAX_PAPERS", "0")) or None
    except Exception:
        MAX_PAPERS = None

# 输出目录（按实验分流）
OUTPUT_DIR = Path(f"E:/langchain/outputs/extractions/{EXP_ID}/deepseek_rag")
LOG_DIR = Path(f"E:/langchain/outputs/logs/{EXP_ID}/deepseek")
PROMPT_EXAMPLE_DIR = PROJECT_ROOT / "data" / "prompts" / "deepseek_rag_examples"  # 仅保存示例 Prompt

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PROMPT_EXAMPLE_DIR, exist_ok=True)

# ------------------------------
# RAG 配置
# ------------------------------
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))  # 检索 Top-K 相关模式
RAG_ENABLED = os.getenv("RAG_ENABLED", "1") == "1"  # 是否启用 RAG

# DeepSeek 配置
MODEL_NAME = "deepseek-chat"
PROVIDER_NAME = "deepseek_rag"

print("=" * 80)
print("🚀 RAG 增强版 DeepSeek 实体关系抽取")
print("=" * 80)
print(f"\n配置:")
print(f"  - RAG 启用: {'是' if RAG_ENABLED else '否'}")
print(f"  - RAG Top-K: {RAG_TOP_K}")
print(f"  - 模型: {MODEL_NAME}")
print(f"  - 实验: {EXP_ID}")
print(f"  - 向量库: {VECTOR_DB_DIR.name}")
print(f"  - 最大篇数: {MAX_PAPERS if MAX_PAPERS else '不限'}")

# ------------------------------
# 初始化 LangChain RAG 系统
# ------------------------------
print(f"\n{'='*80}")
print(f"📥 初始化 RAG 系统")
print(f"{'='*80}")

if RAG_ENABLED:
    try:
        print(f"⏳ 加载 BGE-large-zh-v1.5 Embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-zh-v1.5",
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"✅ Embeddings 加载完成")
        
        print(f"⏳ 连接向量数据库...")
        vectorstore = Chroma(
            persist_directory=str(VECTOR_DB_DIR),
            embedding_function=embeddings,
            collection_name="phm_dependency_patterns_langchain"
        )
        
        # 创建检索器
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": RAG_TOP_K}
        )
        
        pattern_count = vectorstore._collection.count()
        print(f"✅ 向量数据库连接成功")
        print(f"   - 模式总数: {pattern_count}")
        print(f"   - 检索策略: Top-{RAG_TOP_K} 相似度")
        
    except Exception as e:
        print(f"❌ RAG 初始化失败: {e}")
        print(f"   将回退到非 RAG 模式")
        RAG_ENABLED = False
else:
    print(f"ℹ️ RAG 未启用，使用传统模式")

# ------------------------------
# 工具函数
# ------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_schema(schema_path: Path) -> dict:
    """加载 Schema 文件（保留用于未来可能的对比实验）"""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_prompt_template() -> str:
    """加载默认 Prompt 模板文件
    - 实验二（exp02）读取新路径：configs/prompts/exp02/prompt.txt
    - 其他情况保持回退至通用模板（不改动）
    """
    path = EXP02_PROMPT_FILE if EXP_ID == "exp02" else PROMPT_FILE
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_exp03_prompt_for_paper(paper_file: str) -> str | None:
    """为实验三加载逐论文 Prompt，按论文文件名无扩展名匹配 .txt 或 .md"""
    try:
        base = os.path.splitext(os.path.basename(paper_file.replace('priority/', '')))[0]
        candidates = [
            EXP03_PROMPTS_DIR / f"{base}.txt",
            EXP03_PROMPTS_DIR / f"{base}.md",
            EXP03_PROMPTS_DIR / f"{base}_prompt.txt",
            EXP03_PROMPTS_DIR / f"prompt_{base}.txt",
            EXP03_PROMPTS_DIR / f"prompt_{base}.md",
        ]
        for p in candidates:
            if p.exists():
                with open(p, 'r', encoding='utf-8') as f:
                    return f.read()
    except Exception:
        pass
    return None

def extract_abstract(paper_text: str, max_length: int = 500) -> str:
    """提取论文摘要用于检索
    
    优先级：
    1. 明确的摘要章节
    2. Abstract 章节
    3. 前 500 字（跳过标题）
    """
    lines = paper_text.split('\n')
    
    # 查找摘要章节
    abstract_start = -1
    abstract_end = -1
    
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        
        # 找到摘要开始
        if abstract_start == -1:
            if line_lower.startswith('## 摘要') or line_lower.startswith('## abstract'):
                abstract_start = i + 1
                continue
        
        # 找到摘要结束（下一个二级标题）
        if abstract_start != -1 and abstract_end == -1:
            if line.strip().startswith('## ') and i > abstract_start:
                abstract_end = i
                break
    
    # 提取摘要
    if abstract_start != -1:
        if abstract_end == -1:
            abstract_end = min(abstract_start + 20, len(lines))  # 最多 20 行
        
        abstract_lines = lines[abstract_start:abstract_end]
        abstract_text = '\n'.join(abstract_lines).strip()
        
        if len(abstract_text) > 50:  # 有效摘要
            return abstract_text[:max_length]
    
    # 如果没有摘要，使用前 500 字（跳过标题）
    text_start = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('#'):
            text_start = i
            break
    
    content = '\n'.join(lines[text_start:])
    return content[:max_length]

def retrieve_relevant_patterns(query_text: str, top_k: int = RAG_TOP_K) -> list:
    """使用 LangChain 检索相关模式"""
    if not RAG_ENABLED:
        return []
    
    try:
        # 提取摘要用于检索
        abstract = extract_abstract(query_text)
        
        # 使用摘要进行检索
        relevant_docs = retriever.get_relevant_documents(abstract)
        
        patterns = []
        for doc in relevant_docs:
            pattern_info = {
                'semantic_pattern': doc.metadata.get('semantic_pattern', 'N/A'),
                'frequency': doc.metadata.get('frequency', 0),
                'syntactic_path': doc.metadata.get('syntactic_path', 'N/A'),
                'content': doc.page_content
            }
            patterns.append(pattern_info)
        
        return patterns
    except Exception as e:
        print(f"⚠️ 检索失败: {e}")
        return []

def translate_entity_to_chinese(entity: str) -> str:
    """将英文实体类型翻译为中文"""
    translation_map = {
        'Performance Metric': '性能指标',  # 先匹配长词组
        'Model': '模型',
        'model': '模型',  # 小写 model
        'Dataset': '数据集',
        'Problem': '问题',
        'Method': '方法',
        'System': '系统',
        'Technology': '技术',
        'Algorithm': '算法',
        'Data': '数据',
        'Task': '任务',
        'Feature': '特征',
        'Parameter': '参数',
        'Indicator': '指标',
        'Application': '应用',
        'Attribute': '属性',
        'Component': '部件',
        'Fault': '故障',
        'Equipment': '装备',
        'Tool': '工具',
        'Standard': '标准',
        'Process': '流程'
    }
    
    # 逐词翻译（长词组优先匹配）
    for en, zh in translation_map.items():
        entity = entity.replace(en, zh)
    
    return entity

def format_patterns_for_prompt(patterns: list) -> str:
    """将检索到的模式格式化为 Prompt 文本（中文版，无频次）"""
    if not patterns:
        return ""
    
    lines = ["\n  **本论文相关的依存路径模式（从1,481条中动态检索）**\n"]
    lines.append(f"基于论文摘要语义相似度，检索到以下 {len(patterns)} 个最相关的实体关系模式作为参考：\n")
    
    for i, pattern in enumerate(patterns, 1):
        semantic = pattern['semantic_pattern']
        # 翻译为中文
        semantic_cn = translate_entity_to_chinese(semantic)
        lines.append(f"{i}. **{semantic_cn}**")
    
    lines.append("\n💡 **请参考以上模式进行实体关系抽取**，这些模式代表了PHM领域常见的语义关系。\n")
    
    return "\n".join(lines)

def build_enhanced_prompt(paper_text: str, schema: dict, *, paper_file: str | None = None) -> tuple:
    """构建 RAG 增强的 Prompt
    
    Returns:
        (enhanced_prompt, retrieved_patterns)
    """
    # 根据实验选择模板：exp03 优先逐论文模板，否则默认模板
    prompt_template = None
    if EXP_ID == "exp03" and paper_file:
        prompt_template = load_exp03_prompt_for_paper(paper_file)
        if prompt_template:
            print("   🧩 使用 exp03 逐论文 Prompt 模板")
        else:
            print("   ⚠️ 未找到对应 exp03 Prompt，回退到通用模板")
    if not prompt_template:
        prompt_template = load_prompt_template()
    
    # RAG 检索相关模式
    retrieved_patterns = []
    rag_section = ""
    
    if RAG_ENABLED:
        print(f"   🔍 检索相关模式...")
        retrieved_patterns = retrieve_relevant_patterns(paper_text)
        if retrieved_patterns:
            rag_section = format_patterns_for_prompt(retrieved_patterns)
            print(f"   ✅ 检索到 {len(retrieved_patterns)} 个相关模式")
        else:
            print(f"   ⚠️ 未检索到相关模式")
    
    # 填充 Prompt
    # schema_placeholder 留空（不使用 Schema）
    # 只使用 RAG 检索的模式
    enhanced_prompt = prompt_template.replace(
        '{schema_placeholder}', 
        rag_section  # 用 RAG 模式替代 Schema
    ).replace(
        '{full_text_placeholder}',
        paper_text
    )
    
    return enhanced_prompt, retrieved_patterns

def strip_code_fences(s: str) -> str:
    """去除 ```json ... ``` 样式的围栏，并移除语言行"""
    if not isinstance(s, str):
        return s
    s = s.strip()
    
    # 处理 markdown 代码块
    if s.startswith("```") and s.endswith("```"):
        s = s[3:-3].strip()
        # 可能以语言标记开头，比如 "json"
        if "\n" in s:
            first_line, rest = s.split("\n", 1)
            if first_line.strip().lower() in {"json", "js", "javascript"}:
                s = rest
    
    # 处理额外说明文本
    # 查找第一个 { 和最后一个 }
    first_brace = s.find('{')
    last_brace = s.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        s = s[first_brace:last_brace + 1]
    
    return s

def parse_json_response(content: str) -> dict:
    """将模型输出解析为严格 JSON，自动剥离代码围栏和额外文本"""
    if not content:
        raise ValueError("API 返回了空内容")
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        cleaned = strip_code_fences(content)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # 打印详细错误信息
            print(f"\n❌ JSON 解析失败:")
            print(f"   错误: {e}")
            print(f"   原始内容长度: {len(content)} 字符")
            print(f"   清理后内容长度: {len(cleaned)} 字符")
            print(f"   原始内容预览 (前500字符):")
            print(f"   {content[:500]}")
            print(f"   清理后内容预览:")
            print(f"   {cleaned[:500]}")
            raise ValueError(f"无法解析 JSON: {e}。清理后内容: {cleaned[:200]}...")

# ------------------------------
# 初始化 DeepSeek 客户端
# ------------------------------
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ------------------------------
# 加载 Schema
# ------------------------------
print(f"\n{'='*80}")
print(f"📂 加载配置文件")
print(f"{'='*80}")

schema_data = load_schema(SCHEMA_FILE)
print(f"✅ Schema 加载完成")
print(f"   - 实体类型: {len(schema_data.get('entity_types', {}))} 种")
print(f"   - 关系类型: {len(schema_data.get('relation_types', {}))} 种")
print(f"   - 高置信模式: {len(schema_data.get('high_confidence_patterns', []))} 个")

# ------------------------------
# 获取论文列表（按阶段：test → priority_remaining → others）
# ------------------------------
test_dir = PAPERS_DIR / "test"
priority_remaining_dir = PAPERS_DIR / "priority_remaining"
others_dir = PAPERS_DIR / "others"

def _collect_md_files(dir_path: Path, prefix: str) -> list:
    if dir_path.exists():
        return sorted([f"{prefix}/{f}" for f in os.listdir(dir_path) if f.endswith('.md')])
    return []

test_papers = _collect_md_files(test_dir, "test")
priority_remaining_papers = _collect_md_files(priority_remaining_dir, "priority_remaining")
others_papers = _collect_md_files(others_dir, "others")

# 跨阶段整体裁剪以满足 MAX_PAPERS（保持顺序：test → priority_remaining → others）
_all_papers = test_papers + priority_remaining_papers + others_papers
_total_before = len(_all_papers)
if MAX_PAPERS and MAX_PAPERS > 0:
    _allowed = set(_all_papers[:MAX_PAPERS])
    test_papers = [p for p in test_papers if p in _allowed]
    priority_remaining_papers = [p for p in priority_remaining_papers if p in _allowed]
    others_papers = [p for p in others_papers if p in _allowed]
    print(f"🔢 仅处理前 {len(_allowed)} 篇（原 {_total_before} 篇）")

# 兼容后续统计打印（保留 papers 变量）
papers = test_papers + priority_remaining_papers + others_papers

print(f"\n✅ 找到 {len(papers)} 篇论文")
print(f"   - Test 论文: {len(test_papers)} 篇")
print(f"   - Priority Remaining 论文: {len(priority_remaining_papers)} 篇")
print(f"   - Others 论文: {len(others_papers)} 篇")

stages = [
    ("test", test_papers),
    ("priority_remaining", priority_remaining_papers),
    ("others", others_papers),
]

# ------------------------------
# 主处理循环
# ------------------------------
print(f"\n{'='*80}")
print(f"🔄 开始抽取")
print(f"{'='*80}")

success_count = 0
failed_count = 0
extraction_logs = []  # 记录每篇成功抽取的时间日志

_total_to_process = sum(len(s[1]) for s in stages)
_processed_so_far = 0

for _stage_idx, (stage_name, stage_papers) in enumerate(stages):
    if not stage_papers:
        continue
    tqdm.write(f"\n阶段：{stage_name}（{len(stage_papers)} 篇）")
    for j, paper_file in enumerate(tqdm(stage_papers, desc=f"{stage_name} 阶段", unit="篇"), 1):
        i = _processed_so_far + j
        tqdm.write(f"\n[{i}/{_total_to_process}] 处理: {paper_file}")
        
        # 输出按阶段分目录：test/、priority_remain/、others/
        _stage_dir = "priority_remain" if stage_name == "priority_remaining" else stage_name
        output_file = OUTPUT_DIR / _stage_dir / os.path.basename(paper_file).replace('.md', '.json')
        os.makedirs(output_file.parent, exist_ok=True)
        if output_file.exists():
            tqdm.write(f"   ⏭️ 已存在，跳过")
            continue
        
        try:
            # 记录开始时间
            paper_start_time = time.time()
            
            # 1. 读取论文
            if paper_file.startswith('test/'):
                paper_path = PAPERS_DIR / 'test' / os.path.basename(paper_file)
            elif paper_file.startswith('priority_remaining/'):
                paper_path = PAPERS_DIR / 'priority_remaining' / os.path.basename(paper_file)
            elif paper_file.startswith('others/'):
                paper_path = PAPERS_DIR / 'others' / os.path.basename(paper_file)
            else:
                paper_path = PAPERS_DIR / paper_file
            
            with open(paper_path, 'r', encoding='utf-8') as f:
                paper_text = f.read()
            
            tqdm.write(f"   📄 论文长度: {len(paper_text)} 字符")
            
            # 2. 构建 RAG 增强 Prompt
            start_time = time.time()
            enhanced_prompt, retrieved_patterns = build_enhanced_prompt(paper_text, schema_data, paper_file=paper_file)
            prompt_time = time.time() - start_time
            
            tqdm.write(f"   ✅ Prompt 构建完成 ({prompt_time:.2f}s)")
            tqdm.write(f"   📊 Prompt 长度: {len(enhanced_prompt)} 字符")
            
            # 示例 Prompt 不再保存为 txt（仅保存 JSON 结果）
            
            # 3. 调用 DeepSeek API
            tqdm.write(f"   ⏳ 调用 DeepSeek API...")
            api_start = time.time()
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "你是 PHM 领域的知识抽取专家。只输出严格的 JSON，不添加任何解释。"},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            api_time = time.time() - api_start
            content = response.choices[0].message.content
            
            tqdm.write(f"   ✅ API 调用完成 ({api_time:.2f}s)")
            
            # 4. 解析结果
            result = parse_json_response(content)
            
            # 5. 保存结果（干净的格式，只保留 entities 和 relations）
            output_data = {
                "entities": result.get("entities", []),
                "relations": result.get("relations", [])
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            # 计算总抽取时间
            paper_total_time = time.time() - paper_start_time
            
            tqdm.write(f"   ✅ 结果已保存: {output_file.name}")
            tqdm.write(f"   📊 抽取统计: {len(result.get('entities', []))} 实体, {len(result.get('relations', []))} 关系")
            tqdm.write(f"   ⏱️ 总耗时: {paper_total_time:.2f}s")
            
            # 记录成功日志（包含元数据）
            extraction_logs.append({
                "paper": paper_file,
                "timestamp": now_iso(),
                "duration_seconds": round(paper_total_time, 3),
                "entity_count": len(result.get('entities', [])),
                "relation_count": len(result.get('relations', [])),
                "rag_enabled": RAG_ENABLED,
                "rag_top_k": RAG_TOP_K if RAG_ENABLED else 0,
                "retrieved_patterns": [p['semantic_pattern'] for p in retrieved_patterns],
                "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                "total_tokens": getattr(response.usage, 'total_tokens', 0),
                "success": True
            })
            
            success_count += 1
            
        except Exception as e:
            tqdm.write(f"   ❌ 处理失败: {e}")
            extraction_logs.append({
                "paper": paper_file,
                "timestamp": now_iso(),
                "success": False,
                "error": str(e)
            })
            failed_count += 1
        
        # 不再在第 10 篇后询问是否继续
        
        # 延迟（避免 API 限流）
        time.sleep(1)

    _processed_so_far += len(stage_papers)

    # 阶段结束后询问是否继续下一阶段
    if _stage_idx < len(stages) - 1:
        tqdm.write(f"\n{'='*80}")
        tqdm.write(f"⏸️  已完成 {stage_name} 阶段抽取")
        tqdm.write(f"{'='*80}")
        _next_stage_name = stages[_stage_idx + 1][0]
        _ans = input(f"是否继续处理下一阶段（{_next_stage_name}）？(y/n): ").strip().lower()
        if _ans != 'y':
            tqdm.write(f"\n🛑 用户选择停止")
            break
        tqdm.write(f"\n▶️  继续处理...\n")

# ------------------------------
# 总结
# ------------------------------
print(f"\n{'='*80}")
print(f"✅ 抽取完成")
print(f"{'='*80}")
print(f"📊 统计:")
print(f"   - 成功: {success_count}")
print(f"   - 失败: {failed_count}")
print(f"   - 总计: {len(papers)}")
print(f"\n💾 输出目录: {OUTPUT_DIR}")

# 保存抽取时间日志（只记录成功的）
if extraction_logs:
    log_file = LOG_DIR / f"extraction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_papers": len(papers),
            "successful_extractions": success_count,
            "failed_extractions": failed_count,
            "logs": extraction_logs
        }, f, ensure_ascii=False, indent=2)
    print(f"📝 日志已保存: {log_file}")

print(f"{'='*80}")
