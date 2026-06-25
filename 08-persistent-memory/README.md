# P8: 持久化记忆助手

> **学习目标**：Checkpointing、thread_id 会话管理、对话摘要压缩、断点恢复

## 核心概念

### Checkpointing（检查点）

LangGraph 的检查点机制会在**每个节点执行后**自动保存状态。这带来两个关键能力：

1. **断点恢复**：程序崩溃后能从上次的状态继续
2. **会话隔离**：通过 `thread_id` 区分不同用户的对话

### 与 P7 的区别

P7 的 Agent 是无状态的——每次 `invoke` 都是全新的对话。P8 通过 checkpointer 实现了**有状态**的助手，能记住之前的对话。

### 对话摘要压缩

当对话历史过长时，LLM 的上下文窗口会不够用。解决方案：
- 当消息超过阈值时，LLM 自动生成摘要
- 用摘要替代旧消息，节省上下文空间

## 运行方式

```bash
python main.py
```

## 知识点

1. `InMemorySaver()` — 内存级检查点（重启丢失）
2. `SqliteSaver` — SQLite 持久化（重启不丢失）
3. `compile(checkpointer=...)` — 为图添加检查点
4. `config={"configurable": {"thread_id": ...}}` — 会话隔离
5. `graph.get_state(config)` — 查看当前检查点状态

## 与下一项目的关系

P8 的检查点是 P9 Human-in-the-Loop 的基础——`interrupt()` 机制依赖检查点来暂停和恢复执行。
