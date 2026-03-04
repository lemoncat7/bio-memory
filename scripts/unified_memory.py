#!/usr/bin/env python3
"""
Unified Memory System v4.0
整合后的统一记忆系统

结合 bio-memory + three-layer-memory + DNA Memory 的优点：
- 智能检测引擎（自动识别关键信息）
- 三层记忆架构（实体/日志/知识）
- 置信度分层（按需加载）
- 决策日志
- 检查点提取
- DNA Memory 增强:
  - 主动遗忘机制
  - 自动归纳模式
  - 知识图谱关联
  - 动态权重强化
"""

import os
import json
import sys
import re
import uuid
from datetime import datetime, timedelta
from collections import defaultdict

# 目录配置
MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
ENTITIES_DIR = os.path.join(MEMORY_DIR, "entities")
LAYER3_FILE = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
LIFE_DIR = os.path.join(MEMORY_DIR, "life")
DECISIONS_DIR = os.path.join(LIFE_DIR, "decisions")
SNAPSHOT_FILE = os.path.join(MEMORY_DIR, ".snapshot")

# DNA Memory 文件
SHORT_TERM_FILE = os.path.join(MEMORY_DIR, "dna_short_term.json")
LONG_TERM_FILE = os.path.join(MEMORY_DIR, "dna_long_term.json")
PATTERNS_FILE = os.path.join(MEMORY_DIR, "dna_patterns.md")
GRAPH_FILE = os.path.join(MEMORY_DIR, "dna_graph.json")
META_FILE = os.path.join(MEMORY_DIR, "dna_meta.json")

# DNA Memory 配置
DNA_CONFIG = {
    "decay_days": 7,
    "decay_rate": 0.1,
    "forget_threshold": 0.2,
    "reflect_trigger": 20,
    "max_short_term": 100,
    "max_long_term": 500,
}


def init():
    """初始化目录"""
    os.makedirs(ENTITIES_DIR, exist_ok=True)
    os.makedirs(DECISIONS_DIR, exist_ok=True)
    os.makedirs(MEMORY_DIR, exist_ok=True)
    print("✅ Unified Memory System v4.0 初始化完成")
    print(f"   Layer 1 (实体): {ENTITIES_DIR}")
    print(f"   Layer 2 (日志): {MEMORY_DIR}/YYYY-MM-DD.md")
    print(f"   Layer 3 (知识): {LAYER3_FILE}")
    print(f"   Snapshot: {SNAPSHOT_FILE}")
    print(f"   DNA Memory: {MEMORY_DIR}/dna_*.json")


# ============ 智能检测引擎 ============

PATTERNS = {
    "project": [r"开始(写|做|搞)", r"我要", r"新项目", r"启动"],
    "todo": [r"明天", r"后天", r"要开会", r"提醒", r"待办"],
    "preference": [r"我喜欢", r"我不喜欢", r"偏好", r"喜欢.*风格"],
    "decision": [r"决定", r"确定", r"采用", r"选择"],
    "person": [r"叫.*", r"是我.*", r".*人叫"],
    "fact": [r"\d+岁", r"\d+年", r"在.*工作", r"在.*学习"],
}

CONFIDENCE = {
    "high": ["确定", "绝对", "肯定", "就是", "真的"],
    "medium": ["可能", "大概", "应该是", "或许"],
    "low": ["好像", "似乎", "听说", "不确定"],
}


def detect_info(text: str) -> list:
    """自动检测关键信息"""
    detected = []
    
    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                conf = "medium"
                for kw in CONFIDENCE["high"]:
                    if kw in text:
                        conf = "high"
                        break
                for kw in CONFIDENCE["low"]:
                    if kw in text:
                        conf = "low"
                        break
                
                detected.append({
                    "category": category,
                    "confidence": conf,
                    "text": text
                })
                break
    
    return detected


def smart_save(text: str, source: str = "conversation"):
    """智能保存 - 自动检测并分类"""
    detected = detect_info(text)
    
    saved = []
    
    for item in detected:
        category = item["category"]
        confidence = item["confidence"]
        
        if category in ["preference", "person", "fact"]:
            entity = "默认"
            if category == "person":
                match = re.search(r"叫([^的]+)", text)
                if match:
                    entity = match.group(1).strip()
            
            add_entity(entity, category, text, f"{source}:{confidence}")
            saved.append(f"✅ 保存到实体 [{category}]")
    
    if not saved:
        save_daily(text, source)
        saved.append("📝 保存到日记")
    
    return saved


# ============ 三层记忆 ============

def add_entity(entity: str, category: str, fact: str, source: str = "manual"):
    """添加事实到 Layer 1"""
    entity_file = os.path.join(ENTITIES_DIR, f"{entity}.json")
    
    if os.path.exists(entity_file):
        with open(entity_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"entity": entity, "facts": [], "tags": []}
    
    if category not in data.get("tags", []):
        data["tags"] = data.get("tags", []) + [category]
    
    is_duplicate = any(f["content"] == fact and f["status"] == "active" for f in data["facts"])
    if is_duplicate:
        return
    
    data["facts"].append({
        "content": fact,
        "category": category,
        "source": source,
        "timestamp": int(datetime.now().timestamp()),
        "status": "active"
    })
    
    with open(entity_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def search_entities(keyword: str, limit: int = 5):
    """搜索 Layer 1"""
    results = []
    keyword_lower = keyword.lower()
    
    for filename in os.listdir(ENTITIES_DIR):
        if not filename.endswith('.json'):
            continue
        
        # 安全验证：确保路径在允许的目录内
        filepath = os.path.join(ENTITIES_DIR, filename)
        real_path = os.path.realpath(filepath)
        if not real_path.startswith(os.path.realpath(ENTITIES_DIR)):
            continue
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for fact in data.get("facts", []):
            if fact["status"] != "active":
                continue
            if keyword_lower in fact["content"].lower():
                results.append({
                    "entity": data["entity"],
                    "fact": fact["content"],
                    "category": fact.get("category", ""),
                    "timestamp": fact.get("timestamp", 0)
                })
    
    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return results[:limit]


def create_decision(title: str, context: str, options: list, selected: int, reason: str):
    """创建决策日志"""
    decision_id = f"dec-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    decision = {
        "id": decision_id,
        "title": title,
        "context": context,
        "options": options,
        "selected": selected,
        "reason": reason,
        "timestamp": int(datetime.now().timestamp())
    }
    
    filepath = os.path.join(DECISIONS_DIR, f"{decision_id}.json")
    with open(filepath, 'w') as f:
        json.dump(decision, f, indent=2, ensure_ascii=False)
    
    index_file = os.path.join(DECISIONS_DIR, "index.json")
    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            index = json.load(f)
    else:
        index = {"decisions": []}
    
    index["decisions"].append({"id": decision_id, "title": title, "timestamp": decision["timestamp"]})
    
    with open(index_file, 'w') as f:
        json.dump(index, f, indent=2)


def save_daily(content: str, source: str = "conversation"):
    """保存到 Layer 2"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = os.path.join(MEMORY_DIR, f"{today}.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    entry = f"- [{timestamp}] [{source}] {content}\n"
    
    with open(daily_file, 'a', encoding='utf-8') as f:
        f.write(entry)


def extract_checkpoint():
    """从今日日志提取关键信息到 Layer 3"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = os.path.join(MEMORY_DIR, f"{today}.md")
    
    if not os.path.exists(daily_file):
        return
    
    with open(daily_file, 'r') as f:
        content = f.read()
    
    keywords = {
        "成就": ["完成", "✅", "修复", "实现"],
        "学习": ["学到了", "学会了", "研究", "分析"],
        "决策": ["决定", "选择", "采用"],
        "问题": ["问题", "错误", "失败", "bug"]
    }
    
    extracted = {k: [] for k in keywords}
    lines = content.split('\n')
    
    for line in lines:
        for category, patterns in keywords.items():
            if any(p in line for p in patterns) and len(line) > 10:
                extracted[category].append(line.strip())
    
    if any(extracted[k] for k in extracted):
        checkpoint_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with open(LAYER3_FILE, 'a') as f:
            f.write(f"\n## 检查点 {checkpoint_time}\n")
            for category in ["成就", "学习", "决策", "问题"]:
                if extracted[category]:
                    f.write(f"\n### {category}\n")
                    for item in extracted[category][:3]:
                        f.write(f"- {item}\n")


# ============ DNA Memory 增强功能 ============

def dna_load_json(path: str) -> dict:
    """加载 JSON"""
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return {"memories": []}
    return {"memories": []}


def dna_save_json(path: str, data: dict):
    """保存 JSON"""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def dna_gen_id() -> str:
    """生成唯一 ID"""
    return f"mem_{uuid.uuid4().hex[:8]}"


def dna_remember(content: str, m_type: str = "fact", importance: float = 0.5):
    """记录新记忆 (DNA Memory)"""
    memory = {
        "id": dna_gen_id(),
        "type": m_type,
        "content": content,
        "importance": importance,
        "created_at": datetime.now().isoformat(),
        "last_accessed": datetime.now().isoformat(),
        "access_count": 0,
        "tags": [],
        "links": []
    }
    
    data = dna_load_json(SHORT_TERM_FILE)
    
    # 检查上限
    if len(data.get("memories", [])) >= DNA_CONFIG["max_short_term"]:
        data["memories"].sort(key=lambda x: (x.get("importance", 0), x.get("last_accessed", "")))
        data["memories"] = data["memories"][1:]
    
    data["memories"].append(memory)
    dna_save_json(SHORT_TERM_FILE, data)
    
    # 检查自动反思
    if len(data.get("memories", [])) >= DNA_CONFIG["reflect_trigger"]:
        dna_reflect()
    
    print(f"✅ 已记录 DNA 记忆: [{memory['id']}] {content[:50]}...")


def dna_recall(query: str, limit: int = 5):
    """回忆相关记忆 (带动态权重)"""
    results = []
    query_lower = query.lower()
    
    for file in [SHORT_TERM_FILE, LONG_TERM_FILE]:
        data = dna_load_json(file)
        for mem in data.get("memories", []):
            content = mem.get("content", "").lower()
            tags = " ".join(mem.get("tags", [])).lower()
            
            if query_lower in content or query_lower in tags:
                # 动态权重强化
                mem["last_accessed"] = datetime.now().isoformat()
                mem["access_count"] = mem.get("access_count", 0) + 1
                mem["importance"] = min(mem.get("importance", 0.5) + 0.1, 1.0)
                results.append((mem, file))
        
        dna_save_json(file, data)
    
    results.sort(key=lambda x: x[0].get("importance", 0), reverse=True)
    
    if not results:
        print(f"🔍 未找到与 '{query}' 相关的记忆")
        return
    
    for mem, source in results[:limit]:
        source_tag = "短期" if "short" in source else "长期"
        print(f"[{mem['id']}] ({mem['type']}) [{source_tag}] {mem['content'][:60]}... [{mem['importance']:.2f}]")


def dna_reflect():
    """反思归纳 - 从短期记忆提取模式"""
    data = dna_load_json(SHORT_TERM_FILE)
    memories = data.get("memories", [])
    
    if len(memories) < 3:
        print("📝 记忆不足，暂不归纳")
        return 0
    
    # 按类型分组
    by_type = defaultdict(list)
    for mem in memories:
        by_type[mem.get("type", "fact")].append(mem)
    
    patterns = []
    promoted = []
    
    for m_type, mems in by_type.items():
        if len(mems) >= 3:
            contents = [m["content"] for m in mems]
            common_words = set(contents[0].split())
            for c in contents[1:]:
                common_words &= set(c.split())
            
            theme = " ".join(list(common_words)[:5]) if common_words else m_type
            
            pattern = {
                "id": dna_gen_id(),
                "type": "pattern",
                "content": f"[{m_type}类模式] {theme}: 归纳自 {len(mems)} 条记忆",
                "sources": [m["id"] for m in mems],
                "created_at": datetime.now().isoformat(),
                "importance": 0.8,
                "tags": [m_type, "pattern"],
                "links": []
            }
            patterns.append(pattern)
            
            # 高权重记忆升级到长期
            for m in mems:
                if m.get("importance", 0) >= 0.7:
                    promoted.append(m)
    
    if patterns:
        lt = dna_load_json(LONG_TERM_FILE)
        lt["memories"].extend(patterns)
        
        for m in promoted:
            if m["id"] not in [x["id"] for x in lt["memories"]]:
                lt["memories"].append(m)
        
        dna_save_json(LONG_TERM_FILE, lt)
        
        # 保存到 patterns.md
        with open(PATTERNS_FILE, 'a') as f:
            f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} 归纳\n")
            for p in patterns:
                f.write(f"- {p['content']}\n")
        
        print(f"💡 归纳出 {len(patterns)} 个模式，升级 {len(promoted)} 条到长期记忆")
    
    # 🔗 自动发现关联
    discover_and_link(memories)
    
    print("📝 暂未发现新模式")
    return 0


def discover_and_link(memories):
    """自动发现记忆之间的关联"""
    if len(memories) < 2:
        return 0
    
    graph = dna_load_json(GRAPH_FILE)
    if "links" not in graph:
        graph["links"] = []
    
    existing_links = {(link["from"], link["to"]) for link in graph["links"]}
    new_links = 0
    
    # 过滤常见无意义词
    stop_words = {
        "的", "是", "了", "在", "和", "有", "我", "你", "他", "她", "它",
        "这", "那", "都", "也", "就", "要", "会", "可以", "一个", "对话",
        "记录", "memory", "record", "tmp", "file", "content", "importance",
        "created", "updated", "type", "conversation", "project", "fact",
        "学习", "添加", "更新", "修复", "整合", "完成", "处理", "设置"
    }
    
    # 提取关键词（人名、主题等）
    keywords = defaultdict(list)
    for mem in memories:
        content = mem.get("content", "").lower()
        # 简单分词
        words = content.replace("的", " ").replace("是", " ").replace("了", " ").replace("在", " ").split()
        for word in words:
            word = word.strip(".,!?;:()[]{}")
            if len(word) >= 2 and word not in stop_words:
                keywords[word].append(mem["id"])
    
    # 找同一关键词关联的记忆
    for word, mem_ids in keywords.items():
        if len(mem_ids) >= 2:
            for i in range(len(mem_ids)):
                for j in range(i+1, len(mem_ids)):
                    from_id, to_id = mem_ids[i], mem_ids[j]
                    if (from_id, to_id) not in existing_links and from_id != to_id:
                        graph["links"].append({
                            "from": from_id,
                            "to": to_id,
                            "relation": f"都提到'{word}'",
                            "created_at": datetime.now().isoformat()
                        })
                        existing_links.add((from_id, to_id))
                        new_links += 1
    
    if new_links > 0:
        dna_save_json(GRAPH_FILE, graph)
        print(f"🔗 自动发现 {new_links} 个关联")
    
    return new_links


def dna_decay():
    """遗忘衰减 - 清理不重要记忆"""
    data = dna_load_json(SHORT_TERM_FILE)
    now = datetime.now()
    kept, forgotten = [], []
    
    for mem in data.get("memories", []):
        try:
            last = datetime.fromisoformat(mem.get("last_accessed", mem.get("created_at", "")))
            days = (now - last).days
            
            if days >= DNA_CONFIG["decay_days"]:
                mem["importance"] = mem.get("importance", 0.5) - DNA_CONFIG["decay_rate"]
                if mem["importance"] < DNA_CONFIG["forget_threshold"]:
                    forgotten.append(mem)
                    continue
            kept.append(mem)
        except:
            kept.append(mem)
    
    data["memories"] = kept
    dna_save_json(SHORT_TERM_FILE, data)
    print(f"🧹 遗忘 {len(forgotten)} 条，保留 {len(kept)} 条")


def dna_link(id1: str, id2: str, relation: str):
    """建立记忆关联"""
    graph = dna_load_json(GRAPH_FILE)
    if "links" not in graph:
        graph["links"] = []
    
    for link in graph["links"]:
        if link["from"] == id1 and link["to"] == id2:
            print("⚠️ 关联已存在")
            return
    
    graph["links"].append({
        "from": id1,
        "to": id2,
        "relation": relation,
        "created_at": datetime.now().isoformat()
    })
    dna_save_json(GRAPH_FILE, graph)
    print(f"🔗 已关联: {id1} --[{relation}]--> {id2}")


def dna_stats():
    """DNA Memory 统计"""
    st = dna_load_json(SHORT_TERM_FILE)
    lt = dna_load_json(LONG_TERM_FILE)
    graph = dna_load_json(GRAPH_FILE)
    
    print("📊 DNA Memory 统计")
    print(f"   短期记忆: {len(st.get('memories', []))} 条")
    print(f"   长期记忆: {len(lt.get('memories', []))} 条")
    print(f"   记忆关联: {len(graph.get('links', []))} 条")


# ============ 主入口 ============

def retrieve(mode: str = "standard"):
    """按需加载三层记忆"""
    print(f"=== Memory [{mode}] ===")
    
    if mode in ["quick", "standard", "deep"]:
        print("\n[Layer 3] 知识库")
        if os.path.exists(LAYER3_FILE):
            lines = 10 if mode == "quick" else 30
            with open(LAYER3_FILE, 'r') as f:
                print('\n'.join(f.read().split('\n')[:lines]))
    
    if mode in ["standard", "deep"]:
        print("\n[Layer 2] 今日日志")
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = os.path.join(MEMORY_DIR, f"{today}.md")
        if os.path.exists(daily_file):
            lines = 20 if mode == "standard" else 50
            with open(daily_file, 'r') as f:
                print('\n'.join(f.read().split('\n')[:lines]))
    
    if mode == "deep":
        print("\n[Layer 1] 实体")
        if os.path.exists(ENTITIES_DIR):
            for f in os.listdir(ENTITIES_DIR)[:5]:
                print(f"  • {f.replace('.json', '')}")
    
    # DNA Memory 统计
    if mode == "deep":
        print("\n[DNA] 记忆统计")
        dna_stats()


def main():
    if len(sys.argv) < 2:
        print("用法: memory.py {init|add|search|decide|checkpoint|retrieve|save|detect|dna_*}")
        print("")
        print("  基础功能:")
        print("    init              - 初始化目录")
        print("    add <实体> <类别> <事实>")
        print("    search <关键词>   - 搜索实体")
        print("    checkpoint        - 提取检查点")
        print("    retrieve [quick|standard|deep]")
        print("    save <内容> [来源]")
        print("    detect <文本>    - 智能检测信息类型")
        print("")
        print("  DNA Memory 功能:")
        print("    dna_remember <内容> [类型] [重要性]")
        print("    dna_recall <关键词>")
        print("    dna_reflect      - 反思归纳")
        print("    dna_decay        - 遗忘衰减")
        print("    dna_link <id1> <id2> <关系>")
        print("    dna_stats        - 统计信息")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        init()
    elif cmd == "add" and len(sys.argv) >= 5:
        add_entity(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "search" and len(sys.argv) >= 3:
        for r in search_entities(sys.argv[2]):
            print(f"  [{r['entity']}] {r['fact']}")
    elif cmd == "checkpoint":
        extract_checkpoint()
    elif cmd == "retrieve":
        mode = sys.argv[2] if len(sys.argv) > 2 else "standard"
        retrieve(mode)
    elif cmd == "save" and len(sys.argv) >= 3:
        save_daily(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "conversation")
    elif cmd == "detect" and len(sys.argv) >= 3:
        for item in detect_info(sys.argv[2]):
            print(f"  [{item['category']}:{item['confidence']}] {item['text']}")
    elif cmd == "dna_remember" and len(sys.argv) >= 3:
        content = sys.argv[2]
        m_type = sys.argv[3] if len(sys.argv) > 3 else "fact"
        importance = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
        dna_remember(content, m_type, importance)
    elif cmd == "dna_recall" and len(sys.argv) >= 3:
        dna_recall(sys.argv[2])
    elif cmd == "dna_reflect":
        dna_reflect()
    elif cmd == "dna_decay":
        dna_decay()
    elif cmd == "dna_link" and len(sys.argv) >= 5:
        dna_link(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "dna_stats":
        dna_stats()
    else:
        print("参数错误")
        sys.exit(1)


if __name__ == "__main__":
    main()
