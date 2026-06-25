# P5: 智能工具助手

> **学习目标**：@tool 装饰器、bind_tools、工具调用循环、手动工具执行

## 核心概念

### 工具（Tools）

工具是 LLM 可以调用的外部函数。通过工具，LLM 能够：
- 查询实时信息（天气、搜索）
- 执行计算（数学表达式）
- 访问知识库（RAG 检索）

### 工具调用流程

```
用户提问 → LLM 决定调用工具 → 执行工具 → 结果回传 → LLM 基于结果生成最终回复
```

这个流程是一个**循环**：LLM 可能需要多次调用工具才能完成任务。

### 关键概念

| 概念 | 说明 |
|------|------|
| `@tool` 装饰器 | 将普通 Python 函数转为 LangChain 工具 |
| `bind_tools()` | 将工具绑定到 LLM |
| `tool_calls` | LLM 返回的工具调用请求 |
| `ToolMessage` | 工具执行结果的回传消息 |

## 运行方式

```bash
python main.py
```

## 知识点

1. `@tool` 装饰器定义工具
2. 函数文档字符串（docstring）自动成为工具描述
3. 类型注解自动生成参数 schema
4. `llm.bind_tools(tools)` 绑定工具
5. 手动实现工具调用循环（LLM → 工具 → LLM → 回复）

## 与下一项目的关系

P5 手动实现了工具调用循环。P6 进入 LangGraph 后，你将看到 LangGraph 如何用 StateGraph 优雅地实现同样的循环，而 P7 的 ReAct Agent 则是 LangGraph 的标准化工具调用模式。
