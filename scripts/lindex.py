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
    """添加时间索引条目 - 只操作最后一行，影响最小"""
    file_path = l0_get_file()
    date = time_str[:10]  # YYYY-MM-DD
    time_hour = time_str[11:13]  # HH
    
    # 读取现有内容
    lines = []
    if os.path.exists(file_path):
        with open(file_path) as f:
            lines = f.readlines()
    
    # 检查最后一行是否是同一时间段
    last_line = lines[-1] if lines else ""
    prefix = f"- {date} {time_hour}:"
    last_is_same_hour = last_line.strip() and prefix in last_line
    
    if last_is_same_hour:
        # 合并到最后一行 - 去掉前缀提取内容
        existing = last_line.strip()
        if prefix in existing:
            content_part = existing[len(prefix):].strip()
        else:
            content_part = existing
        new_content = content_part + "; " + summary
        lines[-1] = f"{prefix} {new_content}\n"
    else:
        # 不是当前时间段，追加新行
        # 先检查是否需要添加日期标题
        if not lines or f"## {date}" not in "".join(lines[-5:]):
            # 需要添加日期标题
            if lines and lines[-1].strip():
                lines.append("\n")
            lines.append(f"## {date}\n")
        
        # 追加新行
        lines.append(f"- {date} {time_hour}: {summary}\n")
    
    # 写回文件
    with open(file_path, "w") as f:
        f.writelines(lines)
    
    return f"✅ L0 更新: {date} {time_hour}: {summary}"


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
    import re
    file_path = l1_get_file()
    
    # 强大的日期时间解析 - 支持多种格式，强制输出 YYYY-MM-DD HH:MM
    # 支持格式: 
    #   YYYY-MM-DD-HH:MM
    #   YYYY-MM-DD HH:MM
    #   YYYY-MM-DD-HHMM
    #   YYYY-MM-DD
    #   HH:MM
    #   now
    
    # 清理输入
    time_str = time_str.strip().replace(' ', '-')
    
    # 尝试各种模式
    match = None
    patterns = [
        r'^(\d{4})-(\d{1,2})-(\d{1,2})-(\d{1,2}):(\d{2})$',  # YYYY-M-D-H:MM
        r'^(\d{4})-(\d{1,2})-(\d{1,2})-(\d{1,2})(\d{2})$',   # YYYY-M-D-HHMM
        r'^(\d{4})-(\d{1,2})-(\d{1,2})$',                     # YYYY-M-D
        r'^(\d{1,2}):(\d{2})$',                               # HH:MM
    ]
    
    now = datetime.now()
    
    for pattern in patterns:
        match = re.match(pattern, time_str)
        if match:
            break
    
    if match:
        groups = match.groups()
        groups_len = len(groups)
        
        if groups_len == 5:  # YYYY-MM-DD-HH:MM
            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            hour = int(groups[3])
            minute = int(groups[4])
        elif groups_len == 4:  # YYYY-MM-DD-HHMM
            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            hour = int(groups[3][0:2])
            minute = int(groups[3][2:4])
        elif groups_len == 3:  # YYYY-MM-DD
            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            hour, minute = 0, 0
        elif groups_len == 2:  # HH:MM
            year, month, day = now.year, now.month, now.day
            hour, minute = int(groups[0]), int(groups[1])
        else:
            year, month, day = now.year, now.month, now.day
            hour, minute = 0, 0
    else:
        # 默认当前时间
        year, month, day = now.year, now.month, now.day
        hour, minute = 0, 0
    
    # 强制格式化
    date_part = f"{year:04d}-{month:02d}-{day:02d}"
    time_part = f"{hour:02d}:{minute:02d}"
    
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
    
    # 丰满格式（带日期前缀以兼容L0处理）
    entry = f"""{header}- {date_part} {time_part} {topic}
  背景: {background}
  决策: {decision}
  上下文: {code}
  结论: {result}
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
    """搜索决策 - 简单返回匹配的文件"""
    results = []
    for f in os.listdir(DECISIONS_DIR):
        if f.endswith(".md"):
            path = os.path.join(DECISIONS_DIR, f)
            with open(path) as fp:
                content = fp.read()
                if keyword.lower() in content.lower():
                    results.append({"month": f.replace(".md", ""), "match": True})
    return results


def l1_search_detail(keyword: str):
    """搜索决策详情 - 返回具体事件的背景/决策/结论"""
    import re
    
    print(f"\n🔍 L1 详情搜索: {keyword}\n")
    
    # 匹配丰满版 L1 格式
    # - YYYY-MM-DD HH:MM Topic
    #   背景: xxx
    #   决策: xxx
    #   上下文: xxx
    #   结论: xxx
    
    pattern = rf"- (\d{{4}}-\d{{2}}-\d{{2}}) (\d{{2}}:\d{{2}}) ([^\n]+)\n(?:  背景: ([^\n]+)\n)?(?:  决策: ([^\n]+)\n)?(?:  上下文: ([^\n]+)\n)?(?:  结论: ([^\n]+)\n)?"
    
    results = []
    for f in os.listdir(DECISIONS_DIR):
        if f.endswith(".md"):
            path = os.path.join(DECISIONS_DIR, f)
            with open(path) as fp:
                content = fp.read()
                matches = re.findall(pattern, content, re.MULTILINE)
                
                for m in matches:
                    date, time, topic, background, decision, context, conclusion = m
                    if keyword.lower() in topic.lower() or keyword.lower() in (background or "").lower() or keyword.lower() in (conclusion or "").lower():
                        results.append({
                            "date": date,
                            "time": time,
                            "topic": topic.strip(),
                            "background": background.strip() if background else "",
                            "decision": decision.strip() if decision else "",
                            "context": context.strip() if context else "",
                            "conclusion": conclusion.strip() if conclusion else ""
                        })
    
    if not results:
        print(f"未找到包含 '{keyword}' 的 L1 决策")
        return
    
    print(f"找到 {len(results)} 条相关决策:\n")
    for r in results:
        print(f"📌 {r['date']} {r['time']} {r['topic']}")
        if r['background']:
            print(f"   背景: {r['background']}")
        if r['decision']:
            print(f"   决策: {r['decision']}")
        if r['conclusion']:
            print(f"   结论: {r['conclusion']}")
        print()


def l1_when(query: str):
    """模糊日期搜索 - 支持: 今天/昨天/日期/时间"""
    import re
    from datetime import datetime, timedelta
    
    print(f"\n🔍 查询: {query}\n")
    
    now = datetime.now()
    
    # 解析查询
    target_dates = []
    
    query = query.lower().strip()
    
    if "今天" in query:
        target_dates = [now.strftime("%m-%d")]
    elif "昨天" in query:
        yesterday = now - timedelta(days=1)
        target_dates = [yesterday.strftime("%m-%d")]
    else:
        # 尝试解析具体日期
        # 格式: 2026-03-06, 03-06, 19:19, 19
        match_date = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", query)
        if match_date:
            target_dates = [f"{match_date.group(2)}-{match_date.group(3)}"]
        
        match_md = re.search(r"(\d{1,2})-(\d{1,2})", query)
        if match_md:
            target_dates = [f"{match_md.group(1)}-{match_md.group(2)}"]
        
        match_hour = re.search(r"^(\d{1,2})$", query)
        if match_hour:
            # 只搜索某个小时
            hour_str = match_hour.group(1).zfill(2)
            # 当天的这个小时
            target_dates = [now.strftime("%m-%d")]
            hour_filter = hour_str
        else:
            hour_filter = None
    
    # 搜索 L1 决策文件
    pattern = rf"- (\d{{4}}-\d{{2}}-\d{{2}}) (\d{{2}}:\d{{2}}) ([^\n]+)\n(?:  背景: ([^\n]+)\n)?(?:  决策: ([^\n]+)\n)?(?:  上下文: ([^\n]+)\n)?(?:  结论: ([^\n]+)\n)?"
    
    results = []
    for f in os.listdir(DECISIONS_DIR):
        if f.endswith(".md"):
            path = os.path.join(DECISIONS_DIR, f)
            with open(path) as fp:
                content = fp.read()
                matches = re.findall(pattern, content, re.MULTILINE)
                
                for m in matches:
                    date, time, topic, background, decision, context, conclusion = m
                    md = date[5:]  # MM-DD
                    
                    # 检查日期匹配
                    date_match = any(md == td for td in target_dates) if target_dates else True
                    
                    # 检查小时匹配
                    hour_match = True
                    if 'hour_filter' in dir() and hour_filter:
                        hour_match = time.startswith(hour_filter)
                    
                    if date_match and hour_match:
                        results.append({
                            "date": date,
                            "time": time,
                            "topic": topic.strip(),
                            "background": background.strip() if background else "",
                            "decision": decision.strip() if decision else "",
                            "context": context.strip() if context else "",
                            "conclusion": conclusion.strip() if conclusion else ""
                        })
    
    if not results:
        print(f"未找到 {query} 相关的决策")
        return
    
    print(f"找到 {len(results)} 条决策:\n")
    for r in sorted(results, key=lambda x: x["date"] + x["time"], reverse=True):
        print(f"📌 {r['date']} {r['time']} {r['topic']}")
        if r['background']:
            print(f"   背景: {r['background']}")
        if r['decision']:
            print(f"   决策: {r['decision']}")
        if r['conclusion']:
            print(f"   结论: {r['conclusion']}")
        print()


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
    """模糊检索 - 优先级: DNA短期 > L0 > DNA长期"""
    print(f"🔍 搜索: {query}\n")
    
    # 1. DNA 短期记忆 - 最新鲜的记忆，优先返回
    from unified_memory import dna_recall
    print(f"[DNA 短期记忆]")
    dna_recall(query, limit=5, short_only=True)
    
    # 2. L0 时间索引
    l0_results = l0_search(query)
    print(f"\n[L0 时间索引] {len(l0_results)} 个文件")
    if l0_results:
        for r in l0_results:
            print(f"   → {r['month']}: 匹配")
        print("   (详细事件请用: lindex.py process 4)")
    
    # 3. DNA 长期记忆 - 最少被访问
    print(f"\n[DNA 长期记忆]")
    dna_recall(query, limit=3, long_only=True)
    
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
    import re
    
    # 读取当月所有决策文件
    for f in os.listdir(DECISIONS_DIR):
        if f.endswith(".md"):
            month_file = os.path.join(DECISIONS_DIR, f)
            with open(month_file) as fp:
                content = fp.read()
    
    # 匹配 L1 格式: - 2026-03-05 HH:MM 主题
    pattern_l1 = r"- (\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}) ([^\n]+)"
    matches = re.findall(pattern_l1, content)
    
    current_hour = now.hour
    print(f"当前小时: {current_hour}, 最近{hours}小时")
    
    # 筛选最近N小时
    today_str = now.strftime("%m-%d")
    yesterday = now - timedelta(days=1)
    yesterday_str = yesterday.strftime("%m-%d")
    
    for m in matches:
        y, mm, dd, h, m_min, topic = m[0], m[0][5:7], m[0][8:10], m[1], m[2], m[3]
        hour = int(h)
        day = f"{mm}-{dd}"
        
        # 只检查今天或昨天
        if day not in [today_str, yesterday_str]:
            continue
        
        # 判断是否在近N小时
        in_range = False
        if day == yesterday_str:
            # 昨天：需要跨越凌晨
            if current_hour - hours < 0:
                if hour >= current_hour - hours + 24:
                    in_range = True
        elif day == today_str:
            # 今天：正常判断
            if current_hour - hours < 0:
                if hour >= current_hour - hours + 24 or hour <= current_hour:
                    in_range = True
            elif hour >= current_hour - hours and hour <= current_hour:
                in_range = True
        
        if in_range:
            detail = topic[:50]
            decisions.append({"time": f"{h}:{m_min}", "detail": detail.strip(), "date": day})
    
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
    
    # 4. 总结概要录入L0 - 只操作最后一行，影响最小
    if decisions:
        from collections import defaultdict
        
        # 按小时分组
        hour_groups = defaultdict(list)
        for d in decisions:
            hour = d['time'].split(':')[0]
            hour_groups[hour].append(d['detail'][:30])
        
        l0_file = os.path.join(TIMELINE_DIR, f"{now.strftime('%Y-%m')}.md")
        today = now.strftime("%Y-%m-%d")
        
        # 只读取最后一行
        last_line = ""
        if os.path.exists(l0_file):
            with open(l0_file) as f:
                lines = f.readlines()
                last_line = lines[-1] if lines else ""
        
        # 读取所有行用于修改
        lines = []
        if os.path.exists(l0_file):
            with open(l0_file) as f:
                lines = f.readlines()
        
        # 检查最后一行是否是今天当前小时
        current_hour = now.strftime("%H")
        last_is_current = last_line.strip() and f"- {today} {current_hour}:" in last_line
        
            # 按小时排序处理
        for hour in sorted(hour_groups.keys()):
            topics = hour_groups[hour]
            unique = []
            seen = set()
            for t in topics:
                key = t[:20]
                if key not in seen:
                    seen.add(key)
                    unique.append(t)
            summary = f"处理{len(unique)}个决策: {'; '.join(unique[:4])}"
            
            prefix = f"- {today} {hour.zfill(2)}:"
            
            # 检查最后一行是否也是这个小时
            last_is_same_hour = last_line.strip() and f"- {today} {hour.zfill(2)}:" in last_line
            
            if last_is_same_hour:
                # 合并到最后一行 - 去掉前缀，只保留内容
                existing = last_line.strip()
                content_part = existing
                if prefix in content_part:
                    content_part = content_part[len(prefix):].strip()
                new_content = content_part + "; " + summary
                lines[-1] = f"{prefix} {new_content}\n"
            else:
                # 追加新行
                # 先检查是否需要添加日期标题
                if not lines or f"## {today}" not in "".join(lines[-3:]):
                    if lines and lines[-1].strip():
                        lines.append("\n")
                    lines.append(f"## {today}\n")
                lines.append(f"- {today} {hour.zfill(2)}: {summary}\n")
        
        # 写回文件
        with open(l0_file, "w") as f:
            f.writelines(lines)
        
        total = sum(len(v) for v in hour_groups.values())
        print(f"\n✅ L0 更新: {total}条决策，按{len(hour_groups)}个小时分组")
    
    return f"✅ 处理完成: {len(decisions)}条决策已记录并录入L0"


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""L-Index 用法:
  l0 add <时间> <摘要>     - 添加时间索引
  l0 load                - 加载最近时间索引
  l0 search <关键词>     - 搜索时间索引
  
  l1 add <时间> <主题> <背景> <决策> <上下文> <结论> - 添加决策
  l1 load [月份]         - 加载决策
  l1 search <关键词>     - 搜索决策
  
  recent <小时数>         - 获取近N小时的记忆
  
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
            # 格式: l1 add "YYYY-MM-DD-HH:MM" "主题" "背景" "决策" "上下文" "结论"
            time_str = sys.argv[3] if len(sys.argv) > 3 else datetime.now().strftime('%Y-%m-%d-%H-%M')
            topic = sys.argv[4] if len(sys.argv) > 4 else ""
            background = sys.argv[5] if len(sys.argv) > 5 else ""
            decision = sys.argv[6] if len(sys.argv) > 6 else ""
            code = sys.argv[7] if len(sys.argv) > 7 else ""
            result = sys.argv[8] if len(sys.argv) > 8 else ""
            print(l1_add_decision(time_str, topic, background, decision, code, result))
        elif sys.argv[2] == "search":
            for r in l1_search(sys.argv[3]):
                print(f"  {r['month']}: 匹配")
        elif sys.argv[2] == "detail":
            # 格式: l1 detail "关键词"
            keyword = sys.argv[3] if len(sys.argv) > 3 else ""
            l1_search_detail(keyword)
    
    elif cmd == "l2":
        if sys.argv[2] == "update":
            session_file = sys.argv[3] if len(sys.argv) > 3 else ""
            print(l2_update_index(session_file))
        elif sys.argv[2] == "load":
            time_hour = sys.argv[3] if len(sys.argv) > 3 else ""
            print(l2_load_by_time(time_hour)[:500])
    
    elif cmd == "search":
        unified_search(sys.argv[2] if len(sys.argv) > 2 else "")
    
    elif cmd == "detail":
        # 从 L1 获取详情 - 格式: lindex.py detail "关键词"
        keyword = sys.argv[2] if len(sys.argv) > 2 else ""
        l1_search_detail(keyword)
    
    elif cmd == "when":
        # 模糊日期搜索 - 格式: lindex.py when "今天/昨天/日期/时间"
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        l1_when(query)
    
    elif cmd == "recent":
        # 获取近N小时的记忆
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        print(f"\n📅 获取近{hours}小时的记忆:\n")
        
        now = datetime.now()
        current_hour = now.hour
        
        # 搜索 L0
        for f in os.listdir(TIMELINE_DIR):
            if f.endswith(".md"):
                path = os.path.join(TIMELINE_DIR, f)
                with open(path) as fp:
                    content = fp.read()
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('- '):
                            # 匹配 - 2026-03-05 HH: 格式
                            import re
                            match = re.match(r'^- (\d{4}-\d{2}-\d{2}) (\d{2}): (.+)$', line.strip())
                            if match:
                                date, hour, text = match.groups()
                                hour_int = int(hour)
                                # 判断是否在近N小时
                                if current_hour - hours < 0:
                                    if hour_int >= current_hour - hours + 24 or hour_int <= current_hour:
                                        print(f"  {date} {hour}: {text}")
                                elif hour_int >= current_hour - hours and hour_int <= current_hour:
                                    print(f"  {date} {hour}: {text}")
        
        # 搜索 L1
        print("\n📋 决策记录:")
        for f in os.listdir(DECISIONS_DIR):
            if f.endswith(".md"):
                path = os.path.join(DECISIONS_DIR, f)
                with open(path) as fp:
                    content = fp.read()
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('- '):
                            import re
                            match = re.match(r'^- (\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}) (.+)$', line.strip())
                            if match:
                                date, hour, minute, text = match.groups()
                                hour_int = int(hour)
                                if current_hour - hours < 0:
                                    if hour_int >= current_hour - hours + 24 or hour_int <= current_hour:
                                        print(f"  {date} {hour}:{minute} {text}")
                                elif hour_int >= current_hour - hours and hour_int <= current_hour:
                                    print(f"  {date} {hour}:{minute} {text}")
    
    elif cmd == "process":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        print(process_recent_decisions(hours))


if __name__ == "__main__":
    main()
