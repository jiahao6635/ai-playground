# P2: 智能翻译器

> **学习目标**：PromptTemplate、ChatPromptTemplate、Few-shot、结构化输出（Pydantic）

## 核心概念

### Prompt 模板
将变量嵌入提示词模板，避免手动拼接字符串。LangChain 提供 `ChatPromptTemplate` 专门用于聊天模型。

### 结构化输出
通过 `llm.with_structured_output(PydanticModel)`，让 LLM 直接返回 Pydantic 对象，而非原始字符串。这是构建可靠应用的关键技术。

### Few-shot 提示
在提示词中提供几个示例，引导 LLM 学习期望的输出格式和风格。

## 运行方式

```bash
# 基础翻译 + 结构化输出
python main.py

# Few-shot 提示演示
python fewshot.py
```

## 知识点

1. `ChatPromptTemplate.from_messages()` — 构建聊天提示模板
2. `llm.with_structured_output(Model)` — LLM 直接返回 Pydantic 对象
3. `FewShotChatMessagePromptTemplate` — Few-shot 聊天提示模板
4. LCEL 管道操作符 `|` — 链式调用 prompt | llm | parser
5. `StrOutputParser` — 字符串输出解析器

## 与下一项目的关系

P2 掌握了 Prompt 模板和 LCEL 管道后，P3 将深入 **LCEL 的链式组合**，学习并行链、RunnablePassthrough 等高级用法。
