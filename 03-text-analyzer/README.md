# P3: 文本分析管道

> **学习目标**：LCEL（LangChain Expression Language）、Runnable 序列、RunnablePassthrough、RunnableParallel 并行链

## 核心概念

### LCEL — LangChain 表达式语言

LCEL 是 LangChain 的核心设计理念，用 `|` 操作符将组件串联成管道：

```python
chain = prompt | llm | parser
```

这就像 Unix 管道：前一步的输出自动作为后一步的输入。

### 核心组件

| 组件 | 作用 |
|------|------|
| `RunnableSequence` (`\|`) | 顺序执行：A → B → C |
| `RunnablePassthrough` | 透传输入，常用于保留原始数据 |
| `RunnablePassthrough.assign()` | 在输入上追加字段 |
| `RunnableParallel` | 并行执行多个链，结果合并为字典 |
| `itemgetter` | 从字典中提取指定键 |

## 运行方式

```bash
# LCEL 链式调用演示
python main.py

# 并行链演示
python parallel.py
```

## 知识点

1. `prompt | llm | StrOutputParser()` — 基本链
2. `RunnablePassthrough.assign()` — 追加字段到数据流
3. `RunnableParallel` — 并行执行多个分析
4. `itemgetter` — 从输入字典提取字段
5. `with_structured_output()` — 结构化分析报告

## 与下一项目的关系

P3 掌握了 LCEL 后，P4 的 RAG 链将直接使用 LCEL 组合检索器和 LLM。LCEL 是贯穿 LangChain 的核心主线。
