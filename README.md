# Bio-Memory Pro

莫殇的 DNA 记忆系统 + L-Index 三层索引，让 AI 像人类一样记住重要的事情。

## 核心架构

| 系统 | 用途 | 搜索方式 |
|------|------|----------|
| **DNA Memory** | 重要信息/决策记录 | 智能搜索 |
| **L-Index** | 大范围时间索引 | 按时间线 |

## L-Index 三层索引

| 层级 | 名称 | 内容 | 文件位置 |
|------|------|------|----------|
| **L0** | 时间索引 | 时间线摘要 | `memory/timeline/YYYY-MM.md` |
| **L1** | 决策索引 | 关键决策+代码 | `memory/decisions/YYYY-MM.md` |
| **L2** | 完整对话 | 原始JSONL | `memory/dialogue/` |

---

## 快速开始

### 统一入口（推荐）

```bash
cd ~/.openclaw/workspace/skills/bio-memory/scripts
python3 unified_memory.py <命令>
```

### 命令总览

```bash
# 统一搜索（DNA + L0 + L1）
python3 unified_memory.py search "关键词"

# DNA 记忆
python3 unified_memory.py dna_remember "内容" [类型] [权重]
python3 unified_memory.py dna_recall "关键词"
python3 unified_memory.py dna_reflect
python3 unified_memory.py dna_stats

# L-Index
python3 lindex.py l0 add "时间" "摘要"
python3 lindex.py l0
python3 lindex.py l1
python3 lindex.py process 1  # 处理近1小时决策
```

---

## 命令详解

### 1. 统一搜索

```bash
python3 unified_memory.py search "dev1"
```

输出：
```
🔍 搜索: dev1

[L0 时间索引] 1 个文件
[L1 决策索引] 1 个文件
[DNA 记忆]
[mem_eed15109] (preference) [短期] 运维学习环境：dev1...
```

### 2. DNA 记忆

```bash
# 记录记忆
python3 unified_memory.py dna_remember "哥哥说下班了" conversation 0.6

# 搜索记忆
python3 unified_memory.py dna_recall "关键词"

# 反思归纳
python3 unified_memory.py dna_reflect

# 统计
python3 unified_memory.py dna_stats
```

### 3. L-Index

```bash
# L0 - 时间索引
python3 lindex.py l0 add "2026-03-05-09" "处理1个决策: 寂寞陪伴"
python3 lindex.py l0           # 加载最近3个月
python3 lindex.py l0 search "关键词"

# L1 - 决策索引
python3 lindex.py l1 add "主题" "背景" "决策" "代码" "结果"
python3 lindex.py l1          # 加载当月
python3 lindex.py l1 search "关键词"
```

### 4. Process - 处理最近决策（重要！）

获取近N小时决策，记录到DNA并录入L0：

```bash
# 处理近1小时决策
python3 lindex.py process 1

# 处理近2小时决策
python3 lindex.py process 2
```

功能：
1. 获取近N小时决策（L1）
2. 记录到DNA（自动去重）
3. DNA反思 - 判断是否提权
4. 概要录入L0

---

## 定时任务

### Task-Scheduler（推荐）

在 `task-scheduler/scripts/tasks/` 创建任务：

```python
# tasks/process_decisions.py
def register():
    return {
        "name": "process_decisions",
        "interval": 3600,  # 1小时
        "run": process_task
    }

def process_task():
    import os
    bio_dir = os.path.expanduser("~/.openclaw/workspace/skills/bio-memory/scripts")
    result = os.popen(f"cd {bio_dir} && python3 lindex.py process 1").read()
    return f"📊 Process Decisions\n\n{result}"
```

### Cron

```bash
# 每小时执行
0 * * * * cd ~/.openclaw/workspace/skills/bio-memory/scripts && python3 lindex.py process 1
```

---

## 在 HEARTBEAT 中使用

编辑 `~/.openclaw/workspace/HEARTBEAT.md`：

```markdown
## 3. DNA 记忆检查

- 运行: python3 ~/.openclaw/workspace/skills/bio-memory/scripts/unified_memory.py dna_stats
- 如果 > 20 条，运行: python3 ~/.openclaw/workspace/skills/bio-memory/scripts/unified_memory.py dna_reflect

## 4. Process 决策处理

- 运行: python3 ~/.openclaw/workspace/skills/bio-memory/scripts/lindex.py process 1
```

---

## 记忆类型

| 类型 | 说明 | 示例 |
|------|------|------|
| conversation | 对话记录 | 哥哥说下班了 |
| project | 项目相关 | 代码任务 |
| preference | 偏好设置 | 哥哥喜欢咖啡 |
| todo | 待办事项 | 明天要开会 |
| decision | 重要决定 | 确定用这个方案 |

## 权重参考

| 权重 | 场景 |
|------|------|
| 0.9-1.0 | 非常重要 |
| 0.7-0.8 | 比较重要 |
| 0.5-0.6 | 一般 |
| 0.1-0.2 | 可能被遗忘 |

---

## 文件存储

DNA 记忆存储在 `~/.openclaw/workspace/memory/`：

| 文件 | 说明 |
|------|------|
| `dna_short_term.json` | 短期记忆 |
| `dna_long_term.json` | 长期记忆 |
| `dna_patterns.md` | 归纳模式 |
| `dna_graph.json` | 记忆关联 |
| `timeline/YYYY-MM.md` | L0 时间索引 |
| `decisions/YYYY-MM.md` | L1 决策索引 |

---

## ⚠️ 注意事项

1. **参数格式**：必须用空格分隔，不用引号！
   - ✅ `dna_remember 哥哥下班了 conversation 0.6`
   - ❌ `dna_remember "哥哥下班了" conversation 0.6`

2. **Process 去重**：已实现自动去重（短期+长期）

3. **搜索优先级**：DNA短 → L0 → DNA长 → L1 → L2

---

## License

MIT
