#!/usr/bin/env python3
"""
Bio-Memory Pro - 智能 Snapshot 引擎
自动检测关键信息，实时更新记忆
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class SmartSnapshotEngine:
    """智能 Snapshot 引擎 - 自动检测和更新记忆"""
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            self.memory_dir = Path.home() / '.openclaw' / 'workspace' / 'memory'
        else:
            self.memory_dir = Path(memory_dir)
        
        self.snapshot_file = self.memory_dir / '.snapshot.md'
        self.daily_dir = self.memory_dir / 'daily'
        
        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.daily_dir.mkdir(parents=True, exist_ok=True)
    
    # ========== 智能检测规则 ==========
    
    def detect_new_project(self, text: str) -> Optional[Dict]:
        """检测新项目启动"""
        patterns = [
            r'我要开始(.+?)(?:了|吧)?[。！]?$',
            r'准备(?:做|写|弄)(.+?)[。！]?',
            r'启动(.+?)项目',
            r'开个新(.+?)(?:吧)?[。！]?',
            r'写个(.+?)(?:小说|文章|脚本)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                project_name = match.group(1).strip()
                # 清理常见词汇
                project_name = re.sub(r'^(一个|一下|这个|那个)', '', project_name)
                if len(project_name) > 1:
                    return {
                        'type': 'new_project',
                        'name': project_name,
                        'timestamp': datetime.now().isoformat()
                    }
        return None
    
    def detect_todo(self, text: str) -> Optional[Dict]:
        """检测待办事项"""
        patterns = [
            r'(?:待办|todo|TODO)[：:]\s*(.+?)(?:[。！]|$)',
            r'记得(?:要|帮我)?(.+?)(?:[。！]|$)',
            r'别忘了(.+?)(?:[。！]|$)',
            r'(明天|后天|下周|周末|月底)(?:要|得|该)(.+?)(?:[。！]|$)',
            r'(?:需要|应该)(.+?)(?:一下|吧)?[。！]?$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # 处理时间关键词
                if '明天' in text or '后天' in text or '下周' in text:
                    todo_text = text.strip()
                else:
                    groups = match.groups()
                    todo_text = ' '.join(g for g in groups if g).strip()
                
                return {
                    'type': 'todo',
                    'content': todo_text[:100],  # 限制长度
                    'timestamp': datetime.now().isoformat(),
                    'done': False
                }
        return None
    
    def detect_preference(self, text: str) -> Optional[Dict]:
        """检测用户偏好"""
        patterns = [
            r'我(喜欢|爱|偏好|习惯|讨厌|不喜欢)(.+?)(?:[。！]|$)',
            r'(别|不要)(?:太|这么)?(.+?)(?:[。！]|$)',
            r'(.+?)比较适合我',
            r'我对(.+?)感兴趣',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                pref_text = ' '.join(g for g in groups if g).strip()
                return {
                    'type': 'preference',
                    'content': pref_text[:100],
                    'timestamp': datetime.now().isoformat()
                }
        return None
    
    def detect_decision(self, text: str) -> Optional[Dict]:
        """检测重要决定"""
        patterns = [
            r'(?:决定|确定|定下来|说好了)(.+?)(?:[。！]|$)',
            r'(?:方案|计划)(?:是|定为)[:：]?(.+?)(?:[。！]|$)',
            r'就(?:按|用|选)(.+?)(?:吧|了|的)?[。！]?$',
            r'(?:最终|最后)(?:决定|选择)(.+?)(?:[。！]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                decision = match.group(1).strip()
                return {
                    'type': 'decision',
                    'content': decision[:150],
                    'timestamp': datetime.now().isoformat()
                }
        return None
    
    def detect_contact(self, text: str) -> Optional[Dict]:
        """检测人物信息"""
        # 匹配 "我XX叫YYY" 或 "YYY是我的XX"
        patterns = [
            r'我(?:的)?(.+?)(?:叫|是)([^，。！]{2,20})(?:[，。！]|$)',
            r'([^，。！]{2,20})(?:是|叫)我(?:的)?(.+?)(?:[，。！]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                return {
                    'type': 'contact',
                    'relationship': groups[0].strip(),
                    'name': groups[1].strip(),
                    'timestamp': datetime.now().isoformat()
                }
        return None
    
    def analyze_message(self, text: str) -> List[Dict]:
        """分析单条消息，提取所有关键信息"""
        findings = []
        
        detectors = [
            self.detect_new_project,
            self.detect_todo,
            self.detect_preference,
            self.detect_decision,
            self.detect_contact,
        ]
        
        for detector in detectors:
            result = detector(text)
            if result:
                findings.append(result)
        
        return findings
    
    # ========== Snapshot 管理 ==========
    
    def load_snapshot(self) -> Dict:
        """加载当前 snapshot"""
        if not self.snapshot_file.exists():
            return self._create_default_snapshot()
        
        try:
            content = self.snapshot_file.read_text(encoding='utf-8')
            return self._parse_snapshot(content)
        except:
            return self._create_default_snapshot()
    
    def _create_default_snapshot(self) -> Dict:
        """创建默认 snapshot"""
        return {
            'updated_at': datetime.now().isoformat(),
            'active_projects': [],
            'key_context': [],
            'todos': [],
            'important_facts': [
                {'content': '用户: 聪老大', 'added_at': datetime.now().isoformat()},
                {'content': '使用 Bio-Memory Pro 系统', 'added_at': datetime.now().isoformat()},
            ],
            'file_index': {},
        }
    
    def _parse_snapshot(self, content: str) -> Dict:
        """解析 snapshot markdown"""
        # 简化解析，直接返回结构
        snapshot = self._create_default_snapshot()
        
        # 提取更新时间
        match = re.search(r'更新时间[:：]\s*(.+?)(?:\n|$)', content)
        if match:
            snapshot['updated_at'] = match.group(1).strip()
        
        # 提取活跃项目
        projects = re.findall(r'-\s*(.+?)(?:[:：]\s*(.+?))?(?:\n|$)', content)
        for p in projects:
            if p[0] and '项目' in p[0] or '初始化' not in p[0]:
                snapshot['active_projects'].append({
                    'name': p[0].strip(),
                    'status': p[1].strip() if p[1] else '进行中',
                    'added_at': datetime.now().isoformat()
                })
        
        # 提取待办
        todos = re.findall(r'-\s*\[([ x])\]\s*(.+?)(?:\n|$)', content)
        for t in todos:
            snapshot['todos'].append({
                'content': t[1].strip(),
                'done': t[0] == 'x',
                'added_at': datetime.now().isoformat()
            })
        
        return snapshot
    
    def save_snapshot(self, snapshot: Dict):
        """保存 snapshot 为 markdown"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        content = f"""# 记忆快照
更新时间: {now}

## 当前活跃项目
"""
        if snapshot['active_projects']:
            for p in snapshot['active_projects'][-5:]:  # 只保留最近5个
                content += f"- {p['name']}: {p.get('status', '进行中')}\n"
        else:
            content += "- 暂无活跃项目\n"
        
        content += f"""
## 关键上下文
"""
        if snapshot['key_context']:
            for c in snapshot['key_context'][-5:]:
                content += f"- {c['content']}\n"
        else:
            content += "- 暂无关键上下文\n"
        
        content += f"""
## 待办提醒
"""
        active_todos = [t for t in snapshot['todos'] if not t.get('done', False)]
        if active_todos:
            for t in active_todos[-5:]:
                content += f"- [ ] {t['content']}\n"
        else:
            content += "- [ ] 暂无待办\n"
        
        content += f"""
## 重要事实
"""
        for f in snapshot['important_facts'][-10:]:
            content += f"- {f['content']}\n"
        
        content += f"""
## 文件索引
"""
        if snapshot['file_index']:
            for key, path in list(snapshot['file_index'].items())[-5:]:
                content += f"- {key}: {path}\n"
        else:
            content += "- 暂无文件索引\n"
        
        self.snapshot_file.write_text(content, encoding='utf-8')
    
    def update_with_findings(self, findings: List[Dict]) -> List[str]:
        """根据检测结果更新 snapshot，返回更新摘要"""
        if not findings:
            return []
        
        snapshot = self.load_snapshot()
        updates = []
        
        for finding in findings:
            ftype = finding.get('type')
            
            if ftype == 'new_project':
                # 检查是否已存在
                exists = any(p['name'] == finding['name'] 
                           for p in snapshot['active_projects'])
                if not exists:
                    snapshot['active_projects'].append({
                        'name': finding['name'],
                        'status': '新启动',
                        'added_at': finding['timestamp']
                    })
                    updates.append(f"新项目: {finding['name']}")
            
            elif ftype == 'todo':
                # 检查是否重复
                exists = any(t['content'] == finding['content']
                           for t in snapshot['todos'])
                if not exists:
                    snapshot['todos'].append(finding)
                    updates.append(f"新待办: {finding['content'][:30]}...")
            
            elif ftype == 'preference':
                snapshot['important_facts'].append({
                    'content': f"偏好: {finding['content']}",
                    'added_at': finding['timestamp']
                })
                updates.append(f"新偏好: {finding['content'][:30]}...")
            
            elif ftype == 'decision':
                snapshot['key_context'].append({
                    'content': f"决定: {finding['content']}",
                    'added_at': finding['timestamp']
                })
                updates.append(f"新决定: {finding['content'][:30]}...")
            
            elif ftype == 'contact':
                snapshot['important_facts'].append({
                    'content': f"{finding['relationship']}: {finding['name']}",
                    'added_at': finding['timestamp']
                })
                updates.append(f"联系人: {finding['relationship']}-{finding['name']}")
        
        # 更新时间
        snapshot['updated_at'] = datetime.now().isoformat()
        
        # 保存
        self.save_snapshot(snapshot)
        
        return updates
    
    def process_conversation(self, messages: List[Dict]) -> List[str]:
        """处理整个对话，提取并更新记忆"""
        all_findings = []
        
        for msg in messages:
            if msg.get('role') == 'user' and msg.get('content'):
                findings = self.analyze_message(msg['content'])
                all_findings.extend(findings)
        
        return self.update_with_findings(all_findings)


# ========== 快捷函数 ==========

def analyze_and_update(text: str) -> List[str]:
    """分析文本并更新 snapshot，返回更新摘要"""
    engine = SmartSnapshotEngine()
    findings = engine.analyze_message(text)
    return engine.update_with_findings(findings)

def process_session(session_data: List[Dict]) -> List[str]:
    """处理会话数据并更新"""
    engine = SmartSnapshotEngine()
    return engine.process_conversation(session_data)


if __name__ == '__main__':
    # 测试
    test_messages = [
        "我要开始写个新小说，叫《代码觉醒》",
        "记得明天要开会",
        "我喜欢科幻题材",
        "决定用第一人称写",
        "我表妹叫小红",
    ]
    
    engine = SmartSnapshotEngine()
    for msg in test_messages:
        print(f"\n测试: {msg}")
        findings = engine.analyze_message(msg)
        if findings:
            for f in findings:
                print(f"  检测到: {f['type']} - {f.get('name') or f.get('content', '')[:30]}")
        else:
            print("  未检测到关键信息")
