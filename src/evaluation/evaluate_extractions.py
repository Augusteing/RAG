# -*- coding: utf-8 -*-
"""
实体关系抽取结果评估脚本
使用 Gemini 模型对抽取结果进行合理性评估
"""
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from tqdm import tqdm

# OpenAI SDK (Gemini 兼容接口)
from openai import OpenAI

# ------------------------------
# 路径配置
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 评估 Prompt
EVAL_PROMPT_FILE = PROJECT_ROOT / "configs" / "prompts" / "prompt_eva.txt"

# 实验选择：命令行优先，其次环境变量，默认 exp02
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument("--exp", dest="exp_id", choices=["exp02", "exp03"], default=None)
_parser.add_argument("--exp02", dest="exp02", action="store_true")
_parser.add_argument("--exp03", dest="exp03", action="store_true")
_parser.add_argument("--03", dest="exp03_short", action="store_true")
_parser.add_argument("--max", dest="max_items", type=int, default=None, help="仅评估前 N 条结果")
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

# 可选：限制评估数量（命令行 --max 或环境变量 MAX_EVAL）
MAX_ITEMS = _args.max_items
if MAX_ITEMS is None:
    try:
        MAX_ITEMS = int(os.getenv("MAX_EVAL", "0")) or None
    except Exception:
        MAX_ITEMS = None

# 三个模型的抽取结果目录（按实验分流）
DEEPSEEK_DIR = Path(f"E:/langchain/outputs/extractions/{EXP_ID}/deepseek_rag")
GEMINI_DIR = Path(f"E:/langchain/outputs/extractions/{EXP_ID}/gemini_rag")
KIMI_DIR = Path(f"E:/langchain/outputs/extractions/{EXP_ID}/kimi_rag")

# 原始论文目录（用于提供上下文）
PAPERS_DIR = PROJECT_ROOT / "data" / "raw" / "papers"

# 评估结果输出目录（按实验分流）
EVAL_OUTPUT_DIR = Path(f"E:/langchain/outputs/evaluations/{EXP_ID}")
EVAL_LOG_DIR = Path(f"E:/langchain/outputs/logs/{EXP_ID}/evaluation")

os.makedirs(EVAL_OUTPUT_DIR, exist_ok=True)
os.makedirs(EVAL_LOG_DIR, exist_ok=True)

# Gemini 评估配置
EVAL_MODEL = "gemini-2.5-pro"
PROVIDER_NAME = "gemini_evaluator"

# ------------------------------
# 工具函数
# ------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def strip_code_fences(s: str) -> str:
    """去除 ```json ... ``` 样式的代码围栏"""
    if not isinstance(s, str):
        return s
    s = s.strip()
    if s.startswith("```") and s.endswith("```"):
        s = s[3:-3].strip()
        if "\n" in s:
            first_line, rest = s.split("\n", 1)
            if first_line.strip().lower() in {"json", "js", "javascript"}:
                s = rest
    # 尝试提取 { } 之间的内容
    first_brace = s.find('{')
    last_brace = s.rfind('}')
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        s = s[first_brace:last_brace + 1]
    return s

def parse_json_response(content: str) -> dict:
    """解析 JSON 响应,自动清理代码围栏"""
    if not content:
        raise ValueError("API 返回了空内容")
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        cleaned = strip_code_fences(content)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON 解析失败: {e}")
            print(f"   原始内容长度: {len(content)} 字符")
            print(f"   清理后内容长度: {len(cleaned)} 字符")
            print(f"   清理后内容预览: {cleaned[:500]}")
            raise ValueError(f"无法解析 JSON: {e}")

# ------------------------------
# 初始化 Gemini 客户端
# ------------------------------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("请设置 GEMINI_API_KEY 环境变量")

client = OpenAI(
    api_key=api_key,
    base_url="https://hiapi.online/v1"
)

# ------------------------------
# 加载评估 Prompt
# ------------------------------
print(f"📄 加载评估 Prompt: {EVAL_PROMPT_FILE}")
with open(EVAL_PROMPT_FILE, 'r', encoding='utf-8') as f:
    eval_prompt_template = f.read()

print(f"✅ Prompt 长度: {len(eval_prompt_template)} 字符\n")

# ------------------------------
# 评估函数
# ------------------------------
def evaluate_extraction(extraction_data: dict, paper_name: str, model_name: str) -> dict:
    """
    使用 Gemini 评估单个抽取结果
    
    Args:
        extraction_data: 抽取的实体和关系 JSON
        paper_name: 论文名称
        model_name: 抽取模型名称
    
    Returns:
        评估后的 JSON (添加了 evaluation 字段)
    """
    # 构建评估 Prompt
    extraction_json = json.dumps(extraction_data, ensure_ascii=False, indent=2)
    
    eval_prompt = eval_prompt_template + f"""

## 待评估的抽取结果

论文: {paper_name}
抽取模型: {model_name}

```json
{extraction_json}
```

请严格按照要求输出评估后的 JSON,为每个实体和关系添加 `evaluation` 字段。
"""
    
    # 调用 Gemini API
    try:
        response = client.chat.completions.create(
            model=EVAL_MODEL,
            messages=[
                {"role": "system", "content": "你是 PHM 领域的知识抽取评估专家。只输出严格的 JSON，不添加任何解释。"},
                {"role": "user", "content": eval_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        evaluated_data = parse_json_response(content)
        
        # 验证返回格式
        if "entities" not in evaluated_data or "relations" not in evaluated_data:
            raise ValueError(f"返回的 JSON 缺少必需字段: {evaluated_data.keys()}")
        
        return {
            "evaluated_data": evaluated_data,
            "raw_response": content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if hasattr(response, 'usage') else None
        }
        
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        raise

# ------------------------------
# 批量评估
# ------------------------------
def evaluate_model_results(model_name: str, extraction_dir: Path):
    """评估单个模型的所有抽取结果"""
    
    print(f"\n{'='*80}")
    print(f"🔍 评估 {model_name} 模型的抽取结果")
    print(f"{'='*80}")
    
    # 获取所有 JSON 文件
    json_files = sorted(extraction_dir.glob("*.json"))
    # 若指定最大评估条数，进行裁剪
    if MAX_ITEMS and MAX_ITEMS > 0:
        before = len(json_files)
        json_files = json_files[:MAX_ITEMS]
        print(f"🔢 仅评估前 {len(json_files)} 条（原 {before} 条）")
    
    if not json_files:
        print(f"⚠️ 未找到任何 JSON 文件: {extraction_dir}")
        return
    
    print(f"📊 找到 {len(json_files)} 个抽取结果文件")
    
    # 创建模型专用输出目录（如 deepseek/gemini/kimi）
    model_eval_dir = EVAL_OUTPUT_DIR / model_name.lower()
    os.makedirs(model_eval_dir, exist_ok=True)
    
    # 统计信息
    success_count = 0
    failed_count = 0
    total_correct_entities = 0
    total_incorrect_entities = 0
    total_correct_relations = 0
    total_incorrect_relations = 0
    
    # 评估日志
    eval_log = []
    
    # 逐个评估
    for json_file in tqdm(json_files, desc=f"评估 {model_name}"):
        paper_name = json_file.stem
        
        try:
            # 读取抽取结果
            with open(json_file, 'r', encoding='utf-8') as f:
                extraction_data = json.load(f)
            
            # 调用评估
            tqdm.write(f"   📝 评估: {paper_name}")
            start_time = time.time()
            
            eval_result = evaluate_extraction(extraction_data, paper_name, model_name)
            
            eval_time = time.time() - start_time
            
            # 只保存评估后的 JSON 结果
            eval_output_file = model_eval_dir / f"{paper_name}_evaluated.json"
            with open(eval_output_file, 'w', encoding='utf-8') as f:
                json.dump(eval_result['evaluated_data'], f, ensure_ascii=False, indent=2)
            
            # 统计评估结果
            evaluated = eval_result['evaluated_data']
            entities_correct = sum(1 for e in evaluated.get('entities', []) if e.get('evaluation') == '正确')
            entities_incorrect = sum(1 for e in evaluated.get('entities', []) if e.get('evaluation') == '错误')
            relations_correct = sum(1 for r in evaluated.get('relations', []) if r.get('evaluation') == '正确')
            relations_incorrect = sum(1 for r in evaluated.get('relations', []) if r.get('evaluation') == '错误')
            
            total_correct_entities += entities_correct
            total_incorrect_entities += entities_incorrect
            total_correct_relations += relations_correct
            total_incorrect_relations += relations_incorrect
            
            # 记录日志
            log_entry = {
                "time": now_iso(),
                "paper": paper_name,
                "model": model_name,
                "status": "success",
                "eval_time": round(eval_time, 2),
                "entities": {
                    "total": len(evaluated.get('entities', [])),
                    "correct": entities_correct,
                    "incorrect": entities_incorrect,
                    "uncertain": len(evaluated.get('entities', [])) - entities_correct - entities_incorrect
                },
                "relations": {
                    "total": len(evaluated.get('relations', [])),
                    "correct": relations_correct,
                    "incorrect": relations_incorrect,
                    "uncertain": len(evaluated.get('relations', [])) - relations_correct - relations_incorrect
                },
                "usage": eval_result.get('usage'),
                "output_file": str(eval_output_file)
            }
            eval_log.append(log_entry)
            
            tqdm.write(f"   ✅ 实体: {entities_correct}/{len(evaluated.get('entities', []))} 正确, "
                      f"关系: {relations_correct}/{len(evaluated.get('relations', []))} 正确")
            
            success_count += 1
            
            # 避免 API 限流
            time.sleep(1)
            
        except Exception as e:
            tqdm.write(f"   ❌ 失败: {e}")
            
            # 记录失败日志
            log_entry = {
                "time": now_iso(),
                "paper": paper_name,
                "model": model_name,
                "status": "failed",
                "error": str(e)
            }
            eval_log.append(log_entry)
            
            failed_count += 1
            continue
    
    # 保存评估日志
    log_file = EVAL_LOG_DIR / f"{model_name.lower()}_evaluation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(eval_log, f, ensure_ascii=False, indent=2)
    
    # 打印汇总
    print(f"\n{'='*80}")
    print(f"📊 {model_name} 评估汇总")
    print(f"{'='*80}")
    print(f"✅ 成功: {success_count}/{len(json_files)}")
    print(f"❌ 失败: {failed_count}/{len(json_files)}")
    
    if success_count > 0:
        total_entities = total_correct_entities + total_incorrect_entities
        total_relations = total_correct_relations + total_incorrect_relations
        
        entity_accuracy = (total_correct_entities / total_entities * 100) if total_entities > 0 else 0
        relation_accuracy = (total_correct_relations / total_relations * 100) if total_relations > 0 else 0
        
        print(f"\n实体准确率: {entity_accuracy:.2f}% ({total_correct_entities}/{total_entities})")
        print(f"关系准确率: {relation_accuracy:.2f}% ({total_correct_relations}/{total_relations})")
    
    print(f"\n💾 评估日志: {log_file}")
    print(f"📁 评估结果: {model_eval_dir}")
    
    return {
        "model": model_name,
        "success": success_count,
        "failed": failed_count,
        "total": len(json_files),
        "entity_accuracy": entity_accuracy if success_count > 0 else 0,
        "relation_accuracy": relation_accuracy if success_count > 0 else 0,
        "correct_entities": total_correct_entities,
        "incorrect_entities": total_incorrect_entities,
        "correct_relations": total_correct_relations,
        "incorrect_relations": total_incorrect_relations
    }

# ------------------------------
# 主程序
# ------------------------------
def main():
    print("=" * 80)
    print("🔬 实验结果质量评估")
    print("=" * 80)
    print(f"评估模型: {EVAL_MODEL}")
    print(f"实验: {EXP_ID}")
    print(f"最大评估条数: {MAX_ITEMS if MAX_ITEMS else '不限'}")
    print(f"评估 Prompt: {EVAL_PROMPT_FILE.name}")
    print(f"输出目录: {EVAL_OUTPUT_DIR}")
    
    # 评估三个模型
    models_to_evaluate = [
        ("DeepSeek", DEEPSEEK_DIR),
        ("Gemini", GEMINI_DIR),
        ("Kimi", KIMI_DIR)
    ]
    
    all_results = []
    
    for model_name, extraction_dir in models_to_evaluate:
        if not extraction_dir.exists():
            print(f"\n⚠️ 跳过 {model_name}: 目录不存在 ({extraction_dir})")
            continue
        
        result = evaluate_model_results(model_name, extraction_dir)
        all_results.append(result)
    
    # 生成对比报告
    if all_results:
        print("\n" + "=" * 80)
        print("📋 模型评估对比汇总")
        print("=" * 80)
        
        import pandas as pd
        
        summary_df = pd.DataFrame([
            {
                "模型": r["model"],
                "评估成功数": r["success"],
                "评估失败数": r["failed"],
                "实体准确率(%)": round(r["entity_accuracy"], 2),
                "关系准确率(%)": round(r["relation_accuracy"], 2),
                "正确实体数": r["correct_entities"],
                "错误实体数": r["incorrect_entities"],
                "正确关系数": r["correct_relations"],
                "错误关系数": r["incorrect_relations"]
            }
            for r in all_results
        ])
        
        print(summary_df.to_string(index=False))
        
        # 保存汇总
        summary_file = EVAL_OUTPUT_DIR / f"evaluation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 评估汇总已保存: {summary_file}")
    
    print("\n" + "=" * 80)
    print("✅ 评估完成!")
    print("=" * 80)

if __name__ == "__main__":
    main()
