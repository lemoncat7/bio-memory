---
name: bio-memory
description: "莫殇的 DNA 记忆系统 - 自动记录对话、反思归纳、遗忘机制"
license: MIT
---

# Bio-Memory Pro

莫殇专用的记忆系统，让 AI 像人类一样记住重要的事情。

## 核心功能

- **DNA 记忆**：自动记录对话内容到短期记忆
- **反思归纳**：短期记忆 > 20 条自动归纳，升级到长期记忆
- **主动遗忘**：7天未访问的记忆自动衰减，避免信息过载
- **知识图谱**：建立记忆之间的关联

## 文件结构

```
bio-memory/
├── SKILL.md              # 文档
└── scripts/
    ├── unified_memory.py  # 🔥 核心脚本（DNA 记忆）
    ├── smart_snapshot.py  # 智能快照
    └── auto_memory.py     # 自动记忆
```

## 记忆存储目录

DNA 记忆存储在 `~/.openclaw/workspace/memory/`：

| 文件 | 说明 |
|------|------|
| `dna_short_term.json` | 短期记忆 |
| `dna_long_term.json` | 长期记忆 |
| `dna_patterns.md` | 归纳出的模式 |
| `dna_graph.json` | 知识图谱关联 |

## 快速开始

### 记录记忆

```bash
python3 scripts/unified_memory.py dna_remember 内容 类型 权重
```

示例：
```bash
python3 scripts/unified_memory.py dna_remember 哥哥下班了 conversation 0.6
python3 scripts/unified_memory.py dna_remember 哥哥喜欢咖啡 project 0.8
```

### 搜索记忆

```bash
python3 scripts/unified_memory.py dna_recall 关键词
```

### 反思归纳（重要！）

当短期记忆 > 20 条时运行：

```bash
python3 scripts/unified_memory.py dna_reflect
```

效果：
```
💡 归纳出 2 个模式，升级 14 条到长期记忆
```

### 查看统计

```bash
python3 scripts/unified_memory.py dna_stats
```

输出：
```
📊 DNA Memory 统计
   短期记忆: 21 条
   长期记忆: 26 条
   记忆关联: 0 条
```

## 在 HEARTBEAT 中使用

```markdown
## 3. DNA 记忆检查

- 运行: python3 ~/.openclaw/workspace/skills/bio-memory/scripts/unified_memory.py dna_stats
- 如果 > 20 条，运行: python3 ~/.openclaw/workspace/skills/bio-memory/scripts/unified_memory.py dna_reflect
- 如果 > 50 条，运行智能快照: python3 ~/.openclaw/workspace/skills/bio-memory/scripts/smart_snapshot.py
```

## ⚠️ 注意事项

1. **参数格式**：必须用空格分隔，不用引号！
   - ✅ `dna_remember 哥哥下班了 conversation 0.6`
   - ❌ `dna_remember "哥哥下班了" conversation 0.6`

2. **触发阈值**：短期记忆 > 20 条才触发归纳

3. **遗忘机制**：7天未访问的记忆会自动衰减

## 记忆类型

| 类型 | 说明 | 示例 |
|------|------|------|
| conversation | 对话记录 | 日常聊天 |
| project | 项目相关 | 代码任务 |
| preference | 偏好设置 | 哥哥喜欢咖啡 |
| todo | 待办事项 | 明天要开会 |
| decision | 重要决定 | 确定用这个方案 |

## 权重参考

| 权重 | 场景 |
|------|------|
| 0.9-1.0 | 非常重要，必须记住 |
| 0.7-0.8 | 比较重要 |
| 0.5-0.6 | 一般重要 |
| 0.3-0.4 | 轻微重要 |
| 0.1-0.2 | 不太重要，可能被遗忘 |
