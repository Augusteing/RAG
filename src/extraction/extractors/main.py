# -*- coding: utf-8 -*-
"""
主控脚本：串行运行三个模型的知识抽取任务（每个模型独占控制台）
支持：DeepSeek、Gemini、Kimi
特性：处理到第10篇时自动暂停，询问是否继续
设计：一个模型完成后再启动下一个，保持输出清晰
"""
import os
import sys
import subprocess
import time
from datetime import datetime

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 三个模型脚本的路径
SCRIPTS = {
    "deepseek": os.path.join(SCRIPT_DIR, "exact_deepseek.py"),
    "gemini": os.path.join(SCRIPT_DIR, "exact_gemini.py"),
    "kimi": os.path.join(SCRIPT_DIR, "exact_kimi.py")
}

# 模型显示信息
MODEL_DISPLAY = {
    "deepseek": {"name": "DeepSeek", "icon": "🔵"},
    "gemini": {"name": "Gemini", "icon": "🟢"},
    "kimi": {"name": "Kimi", "icon": "🟡"}
}

# 检查所有脚本是否存在
for model_name, script_path in SCRIPTS.items():
    if not os.path.isfile(script_path):
        print(f"❌ 错误：未找到 {model_name} 脚本：{script_path}")
        sys.exit(1)

def run_extraction(model_name: str, script_path: str):
    """运行单个模型的提取任务 - 独占控制台输出"""
    
    start_time = time.time()
    icon = MODEL_DISPLAY[model_name]["icon"]
    name = MODEL_DISPLAY[model_name]["name"]
    
    print("\n" + "╔" + "═"*68 + "╗")
    print(f"║ {icon} {name:^60} {icon} ║")
    print("╠" + "═"*68 + "╣")
    print(f"║ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^56} ║")
    print("╚" + "═"*68 + "╝\n")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['IN_SCOPE_LIMIT'] = '10'
        
        # 临时清除代理设置，避免 SOCKS 错误
        env['HTTP_PROXY'] = ''
        env['HTTPS_PROXY'] = ''
        env['ALL_PROXY'] = ''
        
        # 不捕获输出，让子进程直接显示
        process = subprocess.Popen(
            [sys.executable, script_path],
            env=env
        )
        
        # 等待进程结束
        returncode = process.wait()
        duration = time.time() - start_time
        
        print("\n" + "╔" + "═"*68 + "╗")
        if returncode == 0:
            print(f"║ ✅ {name} 完成！{'':<48} ║")
            status = "✅ 成功"
        else:
            print(f"║ ❌ {name} 失败！退出码: {returncode:<38} ║")
            status = "❌ 失败"
        print(f"║ 耗时: {duration:.2f} 秒{'':<54} ║")
        print("╚" + "═"*68 + "╝\n")
        
        return {
            "model": model_name,
            "status": status,
            "returncode": returncode,
            "duration": duration
        }
    
    except Exception as e:
        duration = time.time() - start_time
        print("\n" + "╔" + "═"*68 + "╗")
        print(f"║ ❌ {name} 运行异常！{'':<46} ║")
        print(f"║ 错误: {str(e)[:60]:<60} ║")
        print("╚" + "═"*68 + "╝\n")
        
        return {
            "model": model_name,
            "status": "❌ 异常",
            "returncode": -1,
            "duration": duration,
            "error": str(e)
        }

def main():
    """主函数：串行运行三个模型"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "🚀 知识图谱抽取 - 多模型串行运行".center(74) + "║")
    print("║" + " "*68 + "║")
    print("╠" + "═"*68 + "╣")
    print(f"║ ⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50} ║")
    print(f"║ 📋 模型列表: {', '.join([MODEL_DISPLAY[m]['name'] for m in SCRIPTS.keys()]):<50} ║")
    print(f"║ ⏸️  暂停机制: 每个模型处理到第 10 篇时将询问是否继续{' '*16} ║")
    print(f"║ 🔄 运行方式: 串行运行（一个接一个，输出清晰不混乱）{' '*16} ║")
    print("╚" + "═"*68 + "╝\n")
    
    # 检查环境变量
    required_keys = {
        "deepseek": ["DEEPSEEK_API_KEY"],
        "gemini": ["HIAPI_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "API_KEY"],
        "kimi": ["KIMI_API_KEY", "MOONSHOT_API_KEY"]
    }
    
    missing_keys = []
    for model, keys in required_keys.items():
        if not any(os.getenv(key) for key in keys):
            missing_keys.append(f"{MODEL_DISPLAY[model]['name']}: {' 或 '.join(keys)}")
    
    if missing_keys:
        print("⚠️  警告：检测到缺失的 API Key：")
        for item in missing_keys:
            print(f"  - {item}")
        print("\n相应模型可能无法运行，请确认环境变量已正确设置。")
        try:
            proceed = input("\n是否继续？(y/n): ").strip().lower()
            if proceed not in {"y", "yes"}:
                print("❌ 用户取消运行。")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n❌ 用户取消运行。")
            return
    
    # 代理设置提示
    if os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY"):
        print("🔧 检测到系统代理设置，将在子进程中临时禁用以避免 SOCKS 错误\n")
    
    overall_start = time.time()
    results = []
    
    # 串行运行每个模型
    for model_name, script_path in SCRIPTS.items():
        result = run_extraction(model_name, script_path)
        results.append(result)
        
        # 如果某个模型失败，询问是否继续下一个
        if result.get("returncode", 0) != 0:
            try:
                answer = input(f"\n⚠️  {MODEL_DISPLAY[model_name]['name']} 运行失败，是否继续运行下一个模型？(y/n): ").strip().lower()
                if answer not in {"y", "yes"}:
                    print("❌ 用户选择停止。")
                    break
            except (EOFError, KeyboardInterrupt):
                print("\n❌ 用户中断。")
                break
    
    overall_duration = time.time() - overall_start
    
    # 汇总报告
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + "🎉 运行完成 - 汇总报告".center(74) + "║")
    print("╠" + "═"*68 + "╣")
    print(f"║ ⏱️  总耗时: {overall_duration:.2f} 秒{'':<51} ║")
    print("╠" + "─"*68 + "╣")
    
    for result in results:
        model = result["model"]
        icon = MODEL_DISPLAY[model]["icon"]
        name = MODEL_DISPLAY[model]["name"]
        status = result["status"]
        duration = result.get("duration", 0)
        returncode = result.get("returncode", -1)
        
        print(f"║ {icon} {name:10} │ {status:8} │ ⏱️  {duration:7.2f}s │ 退出码: {returncode:3}{' '*10} ║")
    
    print("╠" + "═"*68 + "╣")
    print(f"║ 🏁 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50} ║")
    print("╚" + "═"*68 + "╝\n")
    
    if any(r.get("returncode", 0) != 0 for r in results):
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断运行（Ctrl+C）。")
        sys.exit(130)
