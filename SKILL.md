---
name: bio-memory
description: "莫殇的 DNA 记忆系统 + L-Index 三层索引"
license: MIT
---

# Bio-Memory Pro

莫殇的记忆系统 = DNA记忆 + L-Index三层索引

## 核心架构

| 系统 | 用途 | 搜索方式 |
|------|------|----------|
| **DNA Memory** | 重要信息/决策记录 | 智能搜索 |
| **L-Index** | 大范围时间索引 | 按时间线 |

## L-Index 三层索引

| 层级 | 名称 | 内容 | 加载策略 |
|------|------|------|----------|
| **L0** | 时间索引 | 时间线摘要 | 每轮加载 |
| **L1** | 决策索引 | 关键决策+代码 | 按需加载 |
| **L2** | 完整对话 | 原始JSONL | 很少加载 |

### L0 - 时间索引
- 文件: `memory/timeline/YYYY-MM.md`
- 格式:
```markdown
## 2026-03-05
- 02: scheduler优化 - 修复僵尸进程
- 03: L-Index - 实现三层索引
- 09: 处理1个决策: 寂寞陪伴
```

### L1 - 决策索引
- 文件: `memory/decisions/YYYY-MM.md`
- 格式:
```markdown
- 2026-03-06 19:19 memos 是什么
  背景: 哥哥问什么是 memos
  决策: 搜索未找到相关信息，请哥哥提供更多上下文
  上下文:
  结论:
```

### L1 - 获取详情
```bash
# 从 L1 获取具体事件的背景/决策/结论
python3 lindex.py detail "关键词"

# 示例
python3 lindex.py detail "memos"
```

输出：
```
🔍 L1 详情搜索: memos

找到 1 条相关决策:

📌 2026-03-06 19:19 memos 是什么
   背景: 哥哥问什么是 memos
   决策: 搜索未找到相关信息，请哥哥提供更多上下文
```

### L2 - 完整对话
- 来源: `~/.openclaw/agents/main/sessions/`
- 格式: 原始 JSONL

## 文件结构

```
bio-memory/
├── SKILL.md              # 文档
└── scripts/
    ├── unified_memory.py  # 🔥 统一入口（推荐）
    ├── lindex.py          # L-Index 独立命令
    ├── auto_memory.py     # 自动记忆
    └── dna_*.json        # DNA 记忆存储
```

---

## 命令总览

### 推荐：统一入口 `unified_memory.py`

所有功能通过一个入口使用：

```bash
cd ~/.openclaw/workspace/skills/bio-memory/scripts
python3 unified_memory.py <命令>
```

### L-Index 独立命令 `lindex.py`

也可以直接使用 L-Index：

```bash
cd ~/.openclaw/workspace/skills/bio-memory/scripts
python3 lindex.py <命令>
```

---

## 命令详解

### 1. 统一搜索（模糊检索）

```bash
# 搜索所有层（DNA短期 → L0 → DNA长期）
python3 unified_memory.py search "关键词"

# 示例
python3 unified_memory.py search "memos"
```

**搜索优先级**：
1. DNA 短期记忆 - 最新鲜的记忆
2. L0 时间索引 - 按时间定位
3. DNA 长期记忆 - 最少访问的记忆

输出：
```
🔍 搜索: memos

[DNA 短期记忆]
[mem_973fc710] (decision) [短期] 19:19 - memos 是什么... [1.00]

[L0 时间索引] 1 个文件
   → 2026-03: 匹配
   (详细事件请用: lindex.py process 4)

[DNA 长期记忆]
[mem_973fc710] (decision) [长期] 19:19 - memos 是什么... [1.00]

搜索完成
```

---

### 2. DNA 记忆

```bash
# 记录记忆
python3 unified_memory.py dna_remember "内容" [类型] [权重]

# 搜索记忆
python3 unified_memory.py dna_recall "关键词"

# 反思归纳（自动提权到长期）
python3 unified_memory.py dna_reflect

# 统计
python3 unified_memory.py dna_stats
```

#### 示例：记录记忆
```bash
# 记录对话
python3 unified_memory.py dna_remember "哥哥说下班了" conversation 0.6

# 记录偏好
python3 unified_memory.py dna_remember "哥哥喜欢喝咖啡" preference 0.8

# 记录决策
python3 unified_memory.py dna_remember "决定用 L-Index 三层模型" decision 0.9
```

#### 示例：搜索记忆
```bash
python3 unified_memory.py dna_recall "dev1"
```

输出：
```
[mem_eed15109] (preference) [短期] 运维学习环境：dev1 (dev@dev1)，密码dev... [1.00]
[mem_6db3b8c4] (preference) [短期] 哥哥给了弟弟一个运维学习环境dev1... [1.00]
```

#### 示例：统计
```bash
python3 unified_memory.py dna_stats
```

输出：
```
📊 DNA Memory 统计
   短期记忆: 36 条
   长期记忆: 123 条
   记忆关联: 20 条
```

---

### 3. L-Index 命令

#### L0 - 时间索引
```bash
# 添加时间索引
python3 lindex.py l0 add "2026-03-05-09" "处理1个决策: 寂寞陪伴"

# 加载最近3个月
python3 lindex.py l0

# 搜索时间索引
python3 lindex.py l0 search "关键词"
```

#### L1 - 决策索引
```bash
# 添加决策（丰满版）
python3 lindex.py l1 add "主题" "背景" "决策" "上下文" "结论"

# 搜索决策详情
python3 lindex.py detail "关键词"

# 模糊日期搜索
python3 lindex.py when "今天"
python3 lindex.py when "昨天"
python3 lindex.py when "18"
python3 lindex.py when "03-05"
```

#### L2 - 完整对话
```bash
# 更新对话索引
python3 lindex.py l2 update <会话文件>

# 按时间加载对话
python3 lindex.py l2 load "2026-03-05-09"
```

---

### 4. Process - 处理最近决策（重要！）

获取近N小时的决策，记录到DNA并录入L0：

```bash
# 处理近1小时决策
python3 lindex.py process 1

# 处理近2小时决策
python3 lindex.py process 2

# 处理近24小时决策
python3 lindex.py process 24
```

**功能**：
1. 获取近N小时的决策记录（L1）
2. 记录到DNA短期记忆（自动去重）
3. DNA反思 - 判断是否提权到长期记忆
4. 总结概要录入L0

**示例输出**：
```
🔄 处理近2小时的决策记录...

当前小时: 9, 最近2小时
📋 找到 1 条近2小时的决策
📊 当前已有DNA记忆内容数: 100
📝 开始记录 1 条新决策到DNA...
✅ 已记录 DNA 记忆: [mem_2ded03b2] 08:40 - 寂寞陪伴...
✅ L0 录入: 处理1个决策: 寂寞陪伴
✅ 处理完成: 1条决策已记录并录入L0
```

---

## 定时任务

### 方式1：Task-Scheduler（推荐）

在 `task-scheduler/scripts/tasks/` 创建任务文件：

```python
# 示例：process_decisions.py
def register():
    return {
        "name": "process_decisions",
        "interval": 3600,  # 1小时（秒）
        "run": process_task
    }

def process_task():
    import os
    bio_dir = os.path.expanduser("~/.openclaw/workspace/skills/bio-memory/scripts")
    result = os.popen(f"cd {bio_dir} && python3 lindex.py process 1").read()
    return f"📊 Process Decisions\n\n{result}"
```

任务会自动被 scheduler 加载并执行。

---

### 方式2：Cron

```bash
# 每小时执行 process
0 * * * * cd ~/.openclaw/workspace/skills/bio-memory/scripts && python3 lindex.py process 1 >> /var/log/process_decisions.log 2>&1
```

---

## 心跳中使用

### 心跳记录对话

心跳触发时会自动记录对话到 L1 决策索引：

#### 对话记录格式

```markdown
- 2026-03-12 22:38 Matrix房间配置更新
  背景: 哥哥告知房间ID变更
  上下文: 从 UBqTjAJExNAwjFCSHX 改为 fKnRThJZyJIFYFnUud
  决策: 批量更新所有配置文件
  结论: 所有配置已更新完成
```

#### 自动记录流程

心跳执行时会：
1. 调用 `sessions_history(limit=25)` 获取最近消息
2. 过滤出 25 分钟内的真正用户消息（排除 System/Heartbeat）
3. 使用 `echo >>` 追加写入到 `memory/decisions/YYYY-MM.md`
4. 调用 `lindex.py process 1` 将决策录入 DNA 记忆

#### 查看对话记录

```bash
# 按时间查看
python3 lindex.py when "今天"

# 搜索具体事件
python3 lindex.py detail "Matrix"
```

---

### 定时任务 DNA

#### 定时任务列表

| 任务名 | 间隔 | 功能 |
|--------|------|------|
| memory_4h_check | 4小时 | DNA 统计 + 反思 |
| l1_process | 1小时 | 从 L1 处理近1小时决策到 DNA |
| skill_note_4h | 4小时 | 技能笔记处理 |

#### DNA 自动任务

```bash
# DNA 统计（短期记忆 > 20 条时触发反思）
python3 unified_memory.py dna_stats

# 反思归纳（自动提权到长期）
python3 unified_memory.py dna_reflect

# 自动处理 L1 → DNA
python3 lindex.py process 1
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
| fact | 客观事实 | 今天是晴天 |
| skill | 技能学习 | 学了 Python |

## 权重参考

| 权重 | 场景 |
|------|------|
| 0.9-1.0 | 非常重要，必须记住 |
| 0.7-0.8 | 比较重要 |
| 0.5-0.6 | 一般重要 |
| 0.3-0.4 | 轻微重要 |
| 0.1-0.2 | 不太重要，可能被遗忘 |

---

## 文件存储

DNA 记忆存储在 `~/.openclaw/workspace/memory/`：

| 文件 | 说明 |
|------|------|
| `dna_short_term.json` | 短期记忆 |
| `dna_long_term.json` | 长期记忆 |
| `dna_patterns.md` | 归纳出的模式 |
| `dna_graph.json` | 知识图谱关联 |
| `timeline/YYYY-MM.md` | L0 时间索引 |
| `decisions/YYYY-MM.md` | L1 决策索引 |

---

## ⚠️ 注意事项

1. **参数格式**：必须用空格分隔，不用引号！
   - ✅ `dna_remember 哥哥下班了 conversation 0.6`
   - ❌ `dna_remember "哥哥下班了" conversation 0.6`

2. **Process 去重**：已实现自动去重（短期+长期），重复运行不会重复记录

3. **搜索优先级**：
   - `search` → DNA短期 → L0 → DNA长期
   - `detail` → L1 详情搜索（需要知道具体事件背景/结论时用）
   - `when` → 按时间查询 L1（查某天/某时发生了什么）

4. **L1 格式**：
   ```markdown
   - 2026-03-06 19:19 memos 是什么
     背景: 哥哥问什么是 memos
     决策: 搜索未找到相关信息
     上下文:
     结论:
   ```

---

## 命令总览表

| 命令 | 用途 |
|------|------|
| `unified_memory.py search "xxx"` | 模糊检索：DNA短期 → L0 → DNA长期 |
| `lindex.py detail "xxx"` | 从 L1 搜具体事件详情（背景/决策/结论） |
| `lindex.py when "今天/昨天/18/03-05"` | 模糊日期搜索 L1 |
| `lindex.py process 4` | 从 L1 获取近 N 小时事件，喂给 DNA 和 L0 |
| `unified_memory.py dna_remember "内容"` | 记录 DNA 记忆 |
| `unified_memory.py dna_stats` | 查看 DNA 统计 |

