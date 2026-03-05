#!/usr/bin/env python3
"""
L-Index: 三层索引系统
L0: 时间索引 - 每轮加载
L1: 决策索引 - 按需加载
L2: 完整对话 - 很少加载
"""

import os
import json
from datetime import datetime, timedelta

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")

# 目录
TIMELINE_DIR = os.path.join(MEMORY_DIR, "timeline")
DECISIONS_DIR = os.path.join(MEMORY_DIR, "decisions")
DIALOGUE_DIR = os.path.join(MEMORY_DIR, "dialogue")
INDEX_FILE = os.path.join(DIALOGUE_DIR, "index.json")

os.makedirs(TIMELINE_DIR, exist_ok=True)
os.makedirs(DECISIONS_DIR, exist_ok=True)
os.makedirs(DIALOGUE_DIR, exist_ok=True)


# ============ L0: 时间索引 ============

def l0_get_file():
    """获取当前月份的时间索引文件"""
    return os.path.join(TIMELINE_DIR, f"{datetime.now().strftime('%Y-%m')}.md")


def l0_add_entry(time_str: str, summary: str):
    """添加时间索引条目"""
    file_path = l0_get_file()
    date = time_str[:10]  # YYYY-MM-DD
    
    content = ""
    if os.path.exists(file_path):
        with open(file_path) as f:
            content = f.read()
    
    # 检查是否已存在该日期
    if f"## {date}" not in content:
        content += f"\n## {date}\n"
    
    # 使用 HH:MM 格式，支持同一小时多条记录
    time_hour = time_str[11:16]  # HH:MM
    # 直接追加，不检查是否已存在（同小时多条记录）
    content += f"- {time_hour}: {summary}\n"
    
    with open(file_path, "w") as f:
        f.write(content)
    
    return f"✅ L0 添加: {date} {time_hour}: {summary}"


def l0_load_recent(months: int = 3):
    """加载最近几个月的时间索引"""
    results = []
    now = datetime.now()
    
    for i in range(months):
        d = now - timedelta(days=i*30)
        file_path = os.path.join(TIMELINE_DIR, f"{d.strftime('%Y-%m')}.md")
        if os.path.exists(file_path):
            with open(file_path) as f:
                results.append({
                    "month": d.strftime('%Y-%m'),
                    "content": f.read()
                })
    
    return results


def l0_search(keyword: str):
    """搜索时间索引"""
    results = []
    for f in os.listdir(TIMELINE_DIR):
        if f.endswith(".md"):
            path = os.path.join(TIMELINE_DIR, f)
            with open(path) as fp:
                content = fp.read()
                if keyword.lower() in content.lower():
                    results.append({"month": f.replace(".md", ""), "match": True})
    return results


# ============ L1: 决策索引 ============

def l1_get_file():
    """获取当前月份的决策文件"""
    return os.path.join(DECISIONS_DIR, f"{datetime.now().strftime('%Y-%m')}.md")


def l1_add_decision(time_str: str, topic: str, background: str = "", decision: str = "", code: str = "", result: str = ""):
    """添加决策 - 丰满版"""
    file_path = l1_get_file()
    
    # 生成日期部分
    date_part = time_str[:10] if len(time_str) >= 10 else datetime.now().strftime('%Y-%m-%d')
    time_part = time_str[11:16] if len(time_str) >= 16 else datetime.now().strftime('%H:%M')
    
    # 读取现有内容
    existing_content = ""
    if os.path.exists(file_path):
        with open(file_path) as f:
            existing_content = f.read()
    
    # 检查是否已有当天日期标题
    if f"## {date_part}" not in existing_content:
        header = f"\n## {date_part}\n"
    else:
        header = ""
    
    # 丰满格式
    entry = f"""{header}- {time_part} {topic}
  背景: {background}
  决策: {decision}
  代码: {code}
  结果: {result}
"""
    
    with open(file_path, "a") as f:
        f.write(entry)
    
    return f"✅ L1 添加: {time_part} {topic}"


def l1_load(month: str = None):
    """加载指定月份的决策"""
    if month is None:
        month = datetime.now().strftime('%Y-%m')
    
    file_path = os.path.join(DECISIONS_DIR, f"{month}.md")
    
    if os.path.exists(file_path):
        with open(file_path) as f:
            return f.read()
    return ""


def l1_search(keyword: str):
    """搜索决策"""
    results = []
    for f in os.listdir(DECISIONS_DIR):
        if f.endswith(".md"):
            path = os.path.join(DECISIONS_DIR, f)
            with open(path) as fp:
                content = fp.read()
                if keyword.lower() in content.lower():
                    results.append({"month": f.replace(".md", ""), "match": True})
    return results


def l1_recent(hours: int = 1):
    """获取最近N小时的决策"""
    results = []
    now = datetime.now()
    current_hour = now.strftime('%Y-%m-%d-%H')
    
    # 读取当天文件
    today_file = os.path.join(DECISIONS_DIR, f"{now.strftime('%Y-%m')}.md")
    
    if os.path.exists(today_file):
        with open(today_file) as f:
            content = f.read()
        
        # 提取最近1小时的条目
        # 格式: - HH:MM 主题 - 内容
        import re
        pattern = r"- (\d{2}:\d{2}) ([^\n]+)"
        matches = re.findall(pattern, content)
        
        for time_str, text in matches:
            hour = int(time_str.split(':')[0])
            current_hour_int = int(current_hour[-2:])
            
            # 同小时内或上一小时
            if hour == current_hour_int or hour == current_hour_int - 1:
                results.append(f"- {time_str} {text}")
    
    return results


# ============ L2: 完整对话 ============

def l2_update_index(current_session_file: str):
    """更新对话索引 - 在 new/reset 时调用"""
    index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE) as f:
            index = json.load(f)
    
    # 复制会话文件
    if current_session_file and os.path.exists(current_session_file):
        dest_file = os.path.join(DIALOGUE_DIR, os.path.basename(current_session_file))
        
        # 只复制新文件
        if not os.path.exists(dest_file):
            with open(current_session_file) as src:
                content = src.read()
            
            # 提取时间范围
            timestamps = []
            for line in content.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        ts = data.get('timestamp', '')
                        if ts:
                            timestamps.append(ts[:13].replace('T', ' '))  # YYYY-MM-DD-HH
                    except:
                        pass
            
            with open(dest_file, 'w') as f:
                f.write(content)
            
            # 更新索引
            if timestamps:
                start_hour = timestamps[0]
                end_hour = timestamps[-1]
                index[start_hour] = os.path.basename(current_session_file)
                # 如果有结束时间，填充中间小时
                if start_hour != end_hour:
                    index[f"{start_hour}~{end_hour}"] = os.path.basename(current_session_file)
    
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    
    return f"✅ L2 更新索引: {len(index)} 条"


def l2_load_by_time(time_hour: str):
    """按时间加载对话"""
    index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE) as f:
            index = json.load(f)
    
    # 精确匹配或模糊匹配
    session_file = index.get(time_hour)
    
    if session_file:
        path = os.path.join(DIALOGUE_DIR, session_file)
        if os.path.exists(path):
            with open(path) as f:
                return f.read()
    
    return ""


# ============ 统一搜索 ============

def unified_search(query: str):
    """统一搜索"""
    print(f"🔍 搜索: {query}\n")
    
    results = {"l0": [], "l1": [], "dna": [], "l2": []}
    
    # L0 搜索
    l0_results = l0_search(query)
    print(f"[L0 时间索引] {len(l0_results)} 个文件")
    results["l0"] = l0_results
    
    # L1 搜索
    l1_results = l1_search(query)
    print(f"[L1 决策索引] {len(l1_results)} 个文件")
    results["l1"] = l1_results
    
    # DNA 搜索 (调用 DNA Memory)
    from unified_memory import dna_recall
    print(f"[DNA 记忆]")
    dna_recall(query)
    
    print(f"\n搜索完成")


# ============ 处理最近决策 ============

def process_recent_decisions(hours: int = 1):
    """
    处理近N小时的决策记录：
    1. 获取近N小时的决策记录（L1）
    2. 记录到短期记忆（DNA）
    3. 判断是否提权到长期记忆
    4. 总结概要录入L0
    """
    print(f"\n🔄 处理近{hours}小时的决策记录...\n")
    
    # 1. 获取近N小时的决策记录
    now = datetime.now()
    decisions = []
    
    # 读取当月所有决策文件
    for f in os.listdir(DECISIONS_DIR):
        if f.endswith(".md"):
            month_file = os.path.join(DECISIONS_DIR, f)
            with open(month_file) as fp:
                content = fp.read()
        
        # 解析决策条目 - 匹配多种格式:
        # 格式1: ### HH:MM - 主题 (新格式)
        # 格式2: - HH:MM 主题 (旧格式)  
        # 格式3: - HH-MM 主题 (l1_add生成的格式)
        import re
        
        # 尝试匹配新格式 ### HH:MM - 主题
        pattern_new = r"### (\d{2}:\d{2}) - ([^\n]+)"
        matches_new = re.findall(pattern_new, content)
        
        # 尝试匹配旧格式 - HH:MM 主题
        pattern_old = r"- (\d{2}:\d{2}) ([^\n]+(?:\n  [^\n]+)*)"
        matches_old = re.findall(pattern_old, content)
        
        # 尝试匹配 l1_add 格式 - HH-MM 主题
        pattern_l1add = r"- (\d{2})-(\d{2}) ([^\n]+)"
        matches_l1add = re.findall(pattern_l1add, content)
        # 转换为 (HH:MM, 主题) 格式
        matches_l1add = [(f"{h}:{m}", t) for h, m, t in matches_l1add]
        
        # 合并两种格式
        all_matches = matches_new + [(t, d.replace('\n  ', ' ').strip()) for t, d in matches_old] + matches_l1add
        
        current_hour = now.hour
        print(f"当前小时: {current_hour}, 最近{hours}小时")
        for time_str, detail in all_matches:
            hour = int(time_str.split(':')[0])
            # 获取最近N小时的决策 (处理跨天情况)
            if current_hour - hours < 0:
                # 跨天: 0到current_hour + 24到24-(hours-current_hour)
                if hour >= current_hour - hours + 24 or hour <= current_hour:
                    decisions.append({"time": time_str, "detail": detail.strip()})
            elif hour >= current_hour - hours and hour <= current_hour:
                decisions.append({"time": time_str, "detail": detail.strip()})
    
    print(f"📋 找到 {len(decisions)} 条近{hours}小时的决策")
    
    if not decisions:
        return "无新决策需要处理"
    
    # 2. 记录到短期记忆（DNA）- 需去重
    # 直接import调用，避免subprocess导致的状态不一致
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from unified_memory import dna_load_json, dna_save_json, dna_reflect, dna_remember, DNA_CONFIG, SHORT_TERM_FILE, LONG_TERM_FILE
    
    def get_all_dna_contents():
        """获取所有DNA记忆内容"""
        contents = set()
        for f in [SHORT_TERM_FILE, LONG_TERM_FILE]:
            if os.path.exists(f):
                with open(f) as fp:
                    data = json.load(fp)
                    for mem in data.get("memories", []):
                        contents.add(mem.get("content", "")[:80])
        return contents
    
    # ⚠️ 关键：在处理前一次性获取已有内容，后续只在这个集合中检查
    # 这样避免进程内文件多次修改导致的状态不一致
    existing_contents = get_all_dna_contents()
    print(f"📊 当前已有DNA记忆内容数: {len(existing_contents)}")
    
    # 找出需要记录的新决策
    to_remember = []
    for decision in decisions:
        summary = f"{decision['time']} - {decision['detail'][:100]}"
        summary_key = summary[:80]
        if summary_key not in existing_contents:
            to_remember.append(summary)
            existing_contents.add(summary_key)  # 防止同批次重复
    
    # 批量记录（不自动触发反射，等全部添加完再手动触发）
    if to_remember:
        print(f"📝 开始记录 {len(to_remember)} 条新决策到DNA...")
        # 临时禁用自动反射
        original_trigger = DNA_CONFIG.get("reflect_trigger", 10)
        DNA_CONFIG["reflect_trigger"] = 999999  # 设一个很大的值
        
        for summary in to_remember:
            dna_remember(summary, "decision", 0.7)
            print(f"  ✅ DNA记录: {summary[:50]}...")
        
        # 恢复反射配置并手动触发一次
        DNA_CONFIG["reflect_trigger"] = original_trigger
        print("\n🧠 执行DNA反思...")
        dna_reflect()
    else:
        print(f"  ⏭️ 无新决策需要记录")
    
    # 3. DNA 反思
    print("\n🧠 执行DNA反思...")
    from unified_memory import dna_reflect
    dna_reflect()
    
    # 4. 总结概要录入L0
    if decisions:
        # 生成概要
        topics = [d['detail'][:30] for d in decisions]
        summary = f"处理{len(decisions)}个决策: {'; '.join(topics)}"
        
        time_str = now.strftime('%Y-%m-%d-%H')
        l0_add_entry(time_str, summary)
        print(f"\n✅ L0 录入: {summary}")
    
    return f"✅ 处理完成: {len(decisions)}条决策已记录并录入L0"


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""L-Index 用法:
  l0 add <时间> <摘要>     - 添加时间索引
  l0 load                - 加载最近时间索引
  l0 search <关键词>     - 搜索时间索引
  
  l1 add <主题> <内容> <结论> - 添加决策
  l1 load [月份]         - 加载决策
  l1 search <关键词>     - 搜索决策
  
  l2 update <会话文件>   - 更新对话索引
  l2 load <时间>         - 加载对话
  
  search <关键词>        - 统一搜索
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "l0":
        if len(sys.argv) < 3:
            # 加载最近
            for r in l0_load_recent():
                print(f"\n=== {r['month']} ===")
                print(r['content'])
        elif sys.argv[2] == "add":
            time_str = sys.argv[3] if len(sys.argv) > 3 else datetime.now().strftime('%Y-%m-%d-%H')
            summary = sys.argv[4] if len(sys.argv) > 4 else "无摘要"
            print(l0_add_entry(time_str, summary))
        elif sys.argv[2] == "search":
            for r in l0_search(sys.argv[3]):
                print(f"  {r['month']}: 匹配")
    
    elif cmd == "l1":
        if len(sys.argv) < 3:
            print(l1_load())
        elif sys.argv[2] == "add":
            time_str = datetime.now().strftime('%Y-%m-%d-%H-%m')
            topic = sys.argv[3] if len(sys.argv) > 3 else ""
            content = sys.argv[4] if len(sys.argv) > 4 else ""
            conclusion = sys.argv[5] if len(sys.argv) > 5 else ""
            print(l1_add_decision(time_str, topic, content, conclusion))
        elif sys.argv[2] == "search":
            for r in l1_search(sys.argv[3]):
                print(f"  {r['month']}: 匹配")
    
    elif cmd == "l2":
        if sys.argv[2] == "update":
            session_file = sys.argv[3] if len(sys.argv) > 3 else ""
            print(l2_update_index(session_file))
        elif sys.argv[2] == "load":
            time_hour = sys.argv[3] if len(sys.argv) > 3 else ""
            print(l2_load_by_time(time_hour)[:500])
    
    elif cmd == "search":
        unified_search(sys.argv[2] if len(sys.argv) > 2 else "")
    
    elif cmd == "process":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        print(process_recent_decisions(hours))


if __name__ == "__main__":
    main()
