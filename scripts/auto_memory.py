#!/usr/bin/env python3
"""
对话记录自动记忆脚本
在每次心跳对话记录时调用，自动提取关键信息存入 DNA Memory
"""

import os
import sys
import json
import re
from datetime import datetime

MEMORY_FILE = os.path.expanduser("~/.openclaw/workspace/memory/dna_short_term.json")
SCRIPT_DIR = os.path.expanduser("~/.openclaw/workspace/skills/bio-memory/scripts")


def load_memories():
    """加载短期记忆"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"memories": []}
    return {"memories": []}


def save_memories(data):
    """保存短期记忆"""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_duplicate(text: str, memories: list) -> bool:
    """检查是否重复记忆"""
    text_lower = text.lower().strip()
    
    for mem in memories:
        existing = mem.get("content", "").lower().strip()
        # 完全相同
        if text_lower == existing:
            return True
        # 相似度超过 80%（简单比较）
        if existing and text_lower in existing or existing in text_lower:
            return True
        # 共同的关键词超过 5 个
        existing_words = set(existing.split())
        new_words = set(text_lower.split())
        common = existing_words & new_words
        if len(common) >= 5:
            return True
    
    return False


def check_and_reflect():
    """检查是否需要反思归纳"""
    data = load_memories()
    count = len(data.get("memories", []))
    
    if count >= 20:
        print(f"📝 短期记忆达到 {count} 条，触发反思归纳...")
        os.system(f"python3 {SCRIPT_DIR}/unified_memory.py dna_reflect")


def extract_key_points(content: str) -> list:
    """从对话内容提取关键信息"""
    key_points = []
    
    # 提取任务/待办
    todo_patterns = [r"添加.*任务", r"创建.*定时", r"设置.*提醒", r"core.*调度"]
    for pattern in todo_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            key_points.append(("todo", content[:100], 0.8))
            break
    
    # 提取决定/偏好
    decision_patterns = [r"决定", r"采用", r"选择", r"我喜欢", r"我不喜欢", r"整合", r"优化"]
    for pattern in decision_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            key_points.append(("preference", content[:100], 0.9))
            break
    
    # 提取学习/技能
    learn_patterns = [r"学习", r"技能", r"研究", r"分析"]
    for pattern in learn_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            key_points.append(("skill", content[:100], 0.7))
            break
    
    # 提取问题/错误
    error_patterns = [r"问题", r"错误", r"修复", r"bug", r"整合"]
    for pattern in error_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            key_points.append(("error", content[:100], 0.8))
            break
    
    # 如果没有匹配，提取一般对话
    if not key_points:
        key_points.append(("conversation", content[:100], 0.5))
    
    return key_points


def auto_remember(conversation_file: str):
    """从对话记录自动记忆"""
    if not os.path.exists(conversation_file):
        print("⚠️ 对话文件不存在")
        return
    
    with open(conversation_file, 'r') as f:
        content = f.read()
    
    # 提取关键点
    key_points = extract_key_points(content)
    
    data = load_memories()
    memories = data.get("memories", [])
    
    added_count = 0
    skipped_count = 0
    
    for m_type, text, importance in key_points:
        # 去重检查
        if is_duplicate(text, memories):
            skipped_count += 1
            print(f"⏭️ 跳过重复: {text[:40]}...")
            continue
        
        import uuid
        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        
        memory = {
            "id": mem_id,
            "type": m_type,
            "content": text,
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 0,
            "tags": ["heartbeat", "auto"],
            "links": []
        }
        
        memories.append(memory)
        added_count += 1
        print(f"✅ 自动记忆 [{m_type}]: {text[:50]}...")
    
    # 检查上限
    if len(memories) > 100:
        memories.sort(key=lambda x: x.get("importance", 0))
        memories = memories[-100:]
    
    data["memories"] = memories
    save_memories(data)
    
    # 检查是否需要反思
    check_and_reflect()
    
    print(f"📊 当前短期记忆: {len(memories)} 条 (新增: {added_count}, 跳过: {skipped_count})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: auto_memory.py <对话文件路径>")
        sys.exit(1)
    
    auto_remember(sys.argv[1])
