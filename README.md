# Bio-Memory Pro

莫殇的 DNA 记忆系统，让 AI 像人类一样记住重要的事情。

## 功能特点

- **DNA 记忆**：自动记录对话内容到短期记忆
- **反思归纳**：短期记忆 > 20 条自动归纳，升级到长期记忆
- **主动遗忘**：7天未访问的记忆自动衰减，避免信息过载
- **知识图谱**：自动发现记忆之间的关联

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/lemoncat7/bio-memory.git
cd bio-memory
```

### 2. 运行命令

```bash
# 记录记忆
python3 scripts/unified_memory.py dna_remember 你好 conversation 0.7

# 搜索记忆
python3 scripts/unified_memory.py dna_recall 关键词

# 反思归纳（重要！）
python3 scripts/unified_memory.py dna_reflect

# 查看统计
python3 scripts/unified_memory.py dna_stats
```

## 在 OpenClaw 中使用

编辑 `~/.openclaw/workspace/HEARTBEAT.md`，添加：

```markdown
## 3. DNA 记忆检查

- 运行: python3 ~/.openclaw/workspace/skills/bio-memory/scripts/unified_memory.py dna_stats
- 如果 > 20 条，运行: python3 ~/.openclaw/workspace/skills/bio-memory/scripts/unified_memory.py dna_reflect
```

## 参数说明

### dna_remember

```
dna_remember <内容> <类型> <权重>
```

| 参数 | 说明 | 示例 |
|------|------|------|
| 内容 | 要记录的内容 | 哥哥下班了 |
| 类型 | conversation/project/preference/todo | conversation |
| 权重 | 0.1-1.0，越高越重要 | 0.7 |

### dna_reflect

自动执行：
1. 按类型分组记忆
2. 提取共同模式
3. 高权重记忆升级到长期
4. **自动发现记忆关联**

### 权重参考

| 权重 | 场景 |
|------|------|
| 0.9-1.0 | 非常重要 |
| 0.7-0.8 | 比较重要 |
| 0.5-0.6 | 一般 |
| 0.1-0.2 | 可能被遗忘 |

## 记忆存储

DNA 记忆存储在 `~/.openclaw/workspace/memory/`：

| 文件 | 说明 |
|------|------|
| dna_short_term.json | 短期记忆 |
| dna_long_term.json | 长期记忆 |
| dna_patterns.md | 归纳模式 |
| dna_graph.json | 记忆关联 |

## 示例

```bash
# 记录哥哥说话
python3 scripts/unified_memory.py dna_remember 哥哥下班了 conversation 0.7

# 记录项目
python3 scripts/unified_memory.py dna_remember 写一个博客系统 project 0.8

# 记录偏好
python3 scripts/unified_memory.py dna_remember 哥哥喜欢喝咖啡 preference 0.9

# 搜索
python3 scripts/unified_memory.py dna_recall 哥哥
# 输出: 哥哥下班了; 哥哥喜欢喝咖啡

# 统计
python3 scripts/unified_memory.py dna_stats
# 输出:
# 📊 DNA Memory 统计
#    短期记忆: 21 条
#    长期记忆: 30 条
#    记忆关联: 35 条
```

## 注意事项

1. **参数格式**：必须用空格分隔，不用引号！
   - ✅ `dna_remember 哥哥下班了 conversation 0.6`
   - ❌ `dna_remember "哥哥下班了" conversation 0.6`

2. **触发阈值**：短期记忆 > 20 条才触发归纳

3. **遗忘机制**：7天未访问的记忆会自动衰减

## License

MIT
