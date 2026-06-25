"""
P6: 文档审批工作流 — StateGraph 主流程

学习内容：
  1. StateGraph 创建有向图
  2. add_node 添加节点
  3. add_edge 添加固定边
  4. add_conditional_edges 添加条件路由
  5. compile() 编译并执行图

工作流结构：
  START → 起草 → 审查 → ┬─ approved → 发布 → END
                         ├─ needs_revision → 修改 → (回到审查)
                         └─ rejected → END

运行：python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langgraph.graph import StateGraph, START, END

from state import WorkflowState
from nodes import draft_node, review_node, revise_node, publish_node


def route_after_review(state: WorkflowState) -> str:
    """
    条件路由函数：审查后决定下一步。

    返回值对应 add_conditional_edges 中的映射键。
    """
    decision = state.get("status", "needs_revision")
    return decision


def build_workflow():
    """
    构建文档审批工作流图。

    Returns:
        编译好的 LangGraph 可执行图
    """
    # ──────────────────────────────────────────────
    # 1. 创建状态图
    #    StateGraph 需要指定 State 类型
    # ──────────────────────────────────────────────
    workflow = StateGraph(WorkflowState)

    # ──────────────────────────────────────────────
    # 2. 添加节点
    #    每个节点是一个函数：(state) → dict（部分更新）
    # ──────────────────────────────────────────────
    workflow.add_node("draft", draft_node)      # 起草
    workflow.add_node("review", review_node)    # 审查
    workflow.add_node("revise", revise_node)    # 修改
    workflow.add_node("publish", publish_node)  # 发布

    # ──────────────────────────────────────────────
    # 3. 添加边（固定路由）
    #    add_edge(from_node, to_node)
    # ──────────────────────────────────────────────
    # START → 起草（入口）
    workflow.add_edge(START, "draft")

    # 起草 → 审查（固定顺序）
    workflow.add_edge("draft", "review")

    # 发布 → END（终点）
    workflow.add_edge("publish", END)

    # ──────────────────────────────────────────────
    # 4. 添加条件边（动态路由）
    #    add_conditional_edges(
    #        source_node,           # 从哪个节点出发
    #        router_function,        # 路由函数：(state) → str（返回目标节点名）
    #        mapping_dict,           # 可选：路由返回值 → 节点名的映射
    #    )
    #
    #    路由函数返回的字符串：
    #      - 如果提供了 mapping，则匹配 mapping 中的键
    #      - 如果未提供 mapping，则字符串就是目标节点名
    # ──────────────────────────────────────────────
    workflow.add_conditional_edges(
        "review",                    # 从审查节点出发
        route_after_review,          # 路由函数
        {
            "approved": "publish",        # 通过 → 发布
            "needs_revision": "revise",   # 需修改 → 修改
            "rejected": END,              # 拒绝 → 结束
        },
    )

    # 修改 → 审查（修改后重新审查，形成循环）
    workflow.add_edge("revise", "review")

    # ──────────────────────────────────────────────
    # 5. 编译图
    #    编译后才能调用 invoke / stream
    # ──────────────────────────────────────────────
    graph = workflow.compile()

    return graph


def run_workflow(topic: str):
    """运行文档审批工作流"""
    graph = build_workflow()

    # 初始状态
    initial_state = {
        "topic": topic,
        "document": "",
        "draft_count": 0,
        "review_score": 0,
        "review_feedback": "",
        "status": "init",
        "revision_history": [],
    }

    # ──────────────────────────────────────────────
    # 执行图
    # invoke 接收初始状态，返回最终状态
    # ──────────────────────────────────────────────
    print(f"\n  📝 主题: {topic}")
    print(f"  🚀 启动工作流...\n")

    final_state = graph.invoke(initial_state)

    # 打印最终结果
    print(f"\n  {'='*50}")
    print(f"  📊 工作流执行完成")
    print(f"  {'='*50}")
    print(f"\n  📄 最终文档（第{final_state['draft_count']}版）:")
    print(f"  {final_state['document']}")
    print(f"\n  📈 最终评分: {final_state.get('review_score', 'N/A')}")
    print(f"  📌 最终状态: {final_state['status']}")

    history = final_state.get("revision_history", [])
    if history:
        print(f"\n  📋 修改历史:")
        for entry in history:
            print(f"    • {entry}")

    return final_state


def demo_stream():
    """演示：流式查看每个节点的执行过程"""
    print_step("流式执行（查看每个节点状态更新）")

    graph = build_workflow()

    initial_state = {
        "topic": "Python 虚拟环境管理最佳实践",
        "document": "",
        "draft_count": 0,
        "review_score": 0,
        "review_feedback": "",
        "status": "init",
        "revision_history": [],
    }

    # ──────────────────────────────────────────────
    # stream() 逐步返回每个节点执行后的状态更新
    # 相比 invoke()（等全部完成），stream() 能看到执行过程
    # ──────────────────────────────────────────────
    print(f"\n  📝 主题: Python 虚拟环境管理最佳实践")
    print(f"\n  🔄 流式执行中...\n")

    for event in graph.stream(initial_state):
        # event 是一个字典：{node_name: state_update}
        for node_name, state_update in event.items():
            status = state_update.get("status", "?")
            score = state_update.get("review_score", "")
            draft = state_update.get("draft_count", "")

            info = f"状态={status}"
            if score:
                info += f", 评分={score}"
            if draft:
                info += f", 第{draft}版"

            print(f"  📍 节点 [{node_name}]: {info}")


def demo_interactive():
    """交互式：用户输入主题"""
    print_step("交互式工作流")

    print("\n  输入 'quit' 退出\n")

    while True:
        topic = input("  📝 请输入文档主题: ").strip()
        if topic.lower() in ("quit", "exit"):
            break
        if not topic:
            continue

        try:
            run_workflow(topic)
        except Exception as e:
            print(f"\n  ❌ 执行失败: {e}\n")


def main():
    config = get_llm_config()
    print_separator("P6: 文档审批工作流")
    print(f"模型: {config.model_name}\n")

    print("  工作流图:")
    print("  START → 起草 → 审查 → ┬─ 通过 → 发布 → END")
    print("                          ├─ 需修改 → 修改 → (回到审查)")
    print("                          └─ 拒绝 → END\n")

    # 演示 1：流式执行
    demo_stream()

    # 演示 2：交互式
    demo_interactive()

    print("\n✅ P6 演示完成！")
    print("\n💡 关键收获：")
    print("   - StateGraph 用图定义工作流，比 while 循环更清晰")
    print("   - 条件路由让工作流能根据状态动态决策")
    print("   - stream() 能看到每个节点的执行过程")


if __name__ == "__main__":
    main()
