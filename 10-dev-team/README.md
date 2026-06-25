# P10: 多智能体开发团队

> **学习目标**：Supervisor 编排模式、子图（Subgraph）、多智能体协作、流式输出

## 核心概念

### Supervisor 模式

Supervisor 是多智能体系统的核心编排模式：

```
用户需求 → Supervisor（决定分配给谁）
              ├─ PM Agent → 需求分析
              ├─ Dev Agent → 代码实现
              └─ Tester Agent → 测试验证
              ↓
         Supervisor（决定下一步）
              ↓
         ... 循环直到完成 ...
```

Supervisor 本身也是一个 LLM 节点，它根据当前状态决定下一个执行的智能体。

### 子图（Subgraph）

每个智能体作为独立子图运行：
- 有自己的状态和内部逻辑
- 可以是简单的 LLM 调用，也可以是完整的 ReAct Agent
- 作为主图的一个节点嵌入

### 流式输出

`stream_mode` 参数控制流式输出的粒度：
- `"values"` — 每步返回完整状态
- `"updates"` — 每步返回增量更新
- `"messages"` — 实时显示 LLM token 流

## 系统架构

```
START → Supervisor → ┬─ "pm" → PM子图 → Supervisor → ...
                     ├─ "dev" → Dev子图 → Supervisor → ...
                     ├─ "tester" → Tester子图 → Supervisor → ...
                     └─ "FINISH" → END
```

## 运行方式

```bash
python main.py
```

## 知识点

1. Supervisor 路由 — LLM 决定下一个智能体
2. 子图嵌套 — `add_node("name", subgraph)`
3. `stream(stream_mode="updates")` — 实时查看每个智能体的工作
4. 多智能体协作 — PM → Dev → Tester 的完整开发流程

## 知识整合

P10 整合了前面所有项目的知识：
- P2 的 Prompt 模板（Supervisor 和各智能体的系统提示）
- P3 的 LCEL 链（各智能体内部使用）
- P5 的工具调用（Dev Agent 可调用工具）
- P6 的 StateGraph 和条件路由（主图结构）
- P7 的 create_react_agent（子智能体使用）
- P8 的持久化（checkpointer）
