# P1: LLM 对话助手

> **学习目标**：ChatOpenAI 配置（自定义 base_url）、消息类型（System/Human/AI）、流式输出

## 核心概念

LangChain 中与 LLM 交互的最基础模式是通过 **消息（Message）** 列表。每条消息有一个角色：

| 消息类型 | 角色 | 用途 |
|---------|------|------|
| `SystemMessage` | system | 设定 AI 的行为、人设、规则 |
| `HumanMessage` | user | 用户的输入 |
| `AIMessage` | assistant | AI 的回复 |

通过维护一个消息历史列表，可以实现**多轮对话**。

## 运行方式

```bash
# 基础对话（一次性返回）
python main.py

# 流式输出（逐字打印）
python streaming.py
```

## 知识点

1. `get_llm()` — 从公共模块获取配置好的 ChatOpenAI 实例
2. `llm.invoke(messages)` — 一次性返回完整回复
3. `llm.stream(messages)` — 流式逐 token 返回
4. 消息历史列表 — 维护多轮对话上下文

## 与下一项目的关系

P1 理解了 LLM 的输入输出模式后，P2 将引入 **Prompt 模板** 和 **结构化输出**，让 LLM 的输出可控且可解析。
