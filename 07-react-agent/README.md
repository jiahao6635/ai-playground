# P7: ReAct 研究助手

> **学习目标**：create_react_agent 预构建、ToolNode、Agent 循环、条件边路由、手动构建 Agent

## 核心概念

### ReAct 模式

ReAct = Reasoning + Acting（推理 + 行动），是 Agent 的标准模式：

```
思考 → 行动（调用工具）→ 观察（获取结果）→ 思考 → ... → 最终回答
```

### Agent = 带循环的状态图

P5 中我们手动实现了工具调用循环（while 循环）。LangGraph 用图优雅地实现：

```
START → agent → ┬─ (有工具调用) → tools → agent → ...
                └─ (无工具调用) → END
```

这是一个**循环图**：agent → tools → agent → tools → ... → END

### 两种构建方式

| 方式 | 说明 |
|------|------|
| `create_react_agent()` | 预构建，一行代码创建 Agent |
| 手动构建 | 理解底层原理，可自定义 |

## 运行方式

```bash
# 预构建 ReAct Agent
python main.py

# 手动构建 Agent（理解底层）
python custom_agent.py
```

## 知识点

1. `create_react_agent(llm, tools)` — 一行创建 Agent
2. `MessagesState` — 内置消息状态
3. `add_messages` reducer — 消息累加
4. `ToolNode` — 批量执行工具
5. 条件边实现 Agent 循环
6. `stream_mode="values"` — 流式查看消息

## 与下一项目的关系

P7 的 Agent 是无状态的——每次调用独立。P8 将引入 **Checkpointing**（持久化），让 Agent 能记住对话历史，实现跨会话记忆。
