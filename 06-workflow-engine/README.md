# P6: 文档审批工作流

> **学习目标**：StateGraph、State（TypedDict）、Node、Edge、条件路由（add_conditional_edges）

## 核心概念

### LangGraph 三要素

| 概念 | 说明 | 类比 |
|------|------|------|
| **State（状态）** | 在节点间传递的数据容器 | 流水线上的产品 |
| **Node（节点）** | 处理状态并返回更新的函数 | 流水线上的工位 |
| **Edge（边）** | 节点间的连接，决定执行顺序 | 流水线的传送带 |

### 条件路由

`add_conditional_edges` 允许根据状态动态决定下一个节点，这是 LangGraph 最强大的特性：

```
审查节点 → (评分 > 80 ?) → 通过 → 发布
                    ↓ 否
              修改 → 回到审查
```

### 与 P5 的区别

P5 的工具调用循环是手动 `while` 循环。LangGraph 用**图**来定义这种循环，更清晰、更可维护。

## 工作流图

```
START → 起草 → 审查 → ┬─ 通过 → 发布 → END
                      ├─ 需修改 → 修改 → (回到审查)
                      └─ 拒绝 → END
```

## 运行方式

```bash
python main.py
```

## 知识点

1. `StateGraph(State)` — 创建状态图
2. `add_node(name, func)` — 添加节点
3. `add_edge(START, "node")` — 添加固定边
4. `add_conditional_edges(node, router, mapping)` — 添加条件边
5. `compile()` — 编译图
6. `.invoke(initial_state)` — 执行图

## 与下一项目的关系

P6 掌握了 StateGraph 的基本概念后，P7 将用 LangGraph 构建 **ReAct Agent** —— 带工具调用循环的状态图，这是 Agent 的标准模式。
