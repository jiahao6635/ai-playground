# P9: 代码审批系统（Human-in-the-Loop）

> **学习目标**：interrupt() 暂停执行、Command.resume() 恢复执行、人工审批工作流

## 核心概念

### Human-in-the-Loop (HITL)

有些场景需要人工介入决策，例如：
- 代码生成后需要人工审查才能执行
- 敏感操作需要人工确认
- AI 不确定时需要人工指导

LangGraph 通过 `interrupt()` + `Command.resume()` 实现这一能力。

### interrupt / resume 流程

```
LLM 生成代码 → interrupt() 暂停图执行 → 等待人工输入
                                            ↓
                                    人工审查并反馈
                                            ↓
Command.resume(value) → 图恢复执行 → 根据反馈执行或重新生成
```

### 必须配合 Checkpointer

`interrupt()` 依赖 checkpointer 保存暂停点的状态。恢复时从检查点加载状态继续执行。

## 工作流图

```
START → 生成代码 → 等待审批(interrupt) → ┬─ 批准 → 执行 → END
                                          ├─ 拒绝 → 重新生成 → 等待审批
                                          └─ 修改 → 用修改后的代码 → 执行 → END
```

## 运行方式

```bash
python main.py
```

## 知识点

1. `interrupt(value)` — 暂停执行并传递数据给调用者
2. `Command.resume(value)` — 恢复执行并注入人工反馈
3. checkpointer 是 interrupt 的必要条件
4. 条件路由处理人工决策结果

## 与下一项目的关系

P9 展示了单个人工审批环节。P10 将构建多智能体系统，其中每个智能体可以独立运行（甚至也是子图），通过 Supervisor 协调。
