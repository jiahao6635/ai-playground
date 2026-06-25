"""
P10: 多智能体开发团队 — 主编排系统

学习内容：
  1. Supervisor 编排模式 — LLM 决定任务分配
  2. 子图嵌套 — 每个智能体作为子图嵌入主图
  3. 多智能体协作 — PM → Dev → Tester 完整开发流程
  4. 流式输出 — stream_mode="updates" 实时查看进度

系统架构：
  START → Supervisor → ┬─ "pm" → PM子图 → Supervisor → ...
                       ├─ "dev" → Dev子图 → Supervisor → ...
                       ├─ "tester" → Tester子图 → Supervisor → ...
                       └─ "FINISH" → END

每个智能体完成后回到 Supervisor，
Supervisor 根据当前进度决定下一步交给谁，
直到所有工作完成（返回 "FINISH"）。

运行：python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from state import TeamState
from supervisor import supervisor_node, route_from_supervisor
from agents.pm_agent import build_pm_subgraph
from agents.dev_agent import build_dev_subgraph
from agents.tester_agent import build_tester_subgraph


def build_team_graph():
    """
    构建多智能体团队的主图。

    主图结构：
      START → supervisor → ┬─ pm → supervisor → ...
                            ├─ dev → supervisor → ...
                            ├─ tester → supervisor → ...
                            └─ END

    每个智能体是一个子图，作为主图的一个节点。
    智能体执行完毕后回到 supervisor，由 supervisor 决定下一步。
    """
    workflow = StateGraph(TeamState)

    # ──────────────────────────────────────────────
    # 1. 添加 Supervisor 节点
    # ──────────────────────────────────────────────
    workflow.add_node("supervisor", supervisor_node)

    # ──────────────────────────────────────────────
    # 2. 添加各智能体子图作为节点
    #    子图编译后可以直接作为 add_node 的参数
    #    LangGraph 会自动处理状态映射
    # ──────────────────────────────────────────────
    workflow.add_node("pm", build_pm_subgraph())
    workflow.add_node("dev", build_dev_subgraph())
    workflow.add_node("tester", build_tester_subgraph())

    # ──────────────────────────────────────────────
    # 3. 边：START → supervisor
    # ──────────────────────────────────────────────
    workflow.add_edge(START, "supervisor")

    # ──────────────────────────────────────────────
    # 4. 条件边：supervisor → pm / dev / tester / END
    #    route_from_supervisor 返回 "pm" / "dev" / "tester" / END
    # ──────────────────────────────────────────────
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "pm": "pm",
            "dev": "dev",
            "tester": "tester",
            END: END,
        },
    )

    # ──────────────────────────────────────────────
    # 5. 每个智能体执行完毕后回到 supervisor
    #    形成循环：supervisor → agent → supervisor → ...
    # ──────────────────────────────────────────────
    workflow.add_edge("pm", "supervisor")
    workflow.add_edge("dev", "supervisor")
    workflow.add_edge("tester", "supervisor")

    # ──────────────────────────────────────────────
    # 6. 编译（带 checkpointer 支持断点恢复）
    # ──────────────────────────────────────────────
    checkpointer = InMemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph


def run_team(request: str):
    """运行多智能体团队完成开发任务"""
    graph = build_team_graph()

    config = {"configurable": {"thread_id": "dev_team"}}

    # 初始状态
    initial_state = {
        "messages": [HumanMessage(content=request)],
        "user_request": request,
        "requirements": "",
        "code": "",
        "test_results": "",
        "next_agent": "",
        "iteration": 0,
    }

    print(f"\n  📝 用户需求: {request}")
    print(f"\n  🚀 启动多智能体团队...\n")

    # ──────────────────────────────────────────────
    # 使用 stream 实时查看每个智能体的工作
    # stream_mode="updates" 每步返回增量更新
    # ──────────────────────────────────────────────
    for event in graph.stream(initial_state, config=config, stream_mode="updates"):
        for node_name, state_update in event.items():
            if node_name == "supervisor":
                next_agent = state_update.get("next_agent", "?")
                iteration = state_update.get("iteration", 0)
                print(f"\n  {'━'*60}")
                print(f"  🎯 [Supervisor] 第 {iteration} 轮 → 交给 [{next_agent}]")
                print(f"  {'━'*60}")

            elif node_name == "pm":
                req = state_update.get("requirements", "")
                print(f"\n  📋 [PM] 需求分析:")
                print(f"  {req[:200]}{'...' if len(req) > 200 else ''}")

            elif node_name == "dev":
                code = state_update.get("code", "")
                print(f"\n  💻 [Dev] 代码生成:")
                print(f"  {code[:300]}{'...' if len(code) > 300 else ''}")

            elif node_name == "tester":
                results = state_update.get("test_results", "")
                print(f"\n  🧪 [Tester] 测试结果:")
                print(f"  {results[:300]}{'...' if len(results) > 300 else ''}")

    # ──────────────────────────────────────────────
    # 获取最终状态
    # ──────────────────────────────────────────────
    final_state = graph.get_state(config)

    print(f"\n  {'='*60}")
    print(f"  📊 开发流程完成")
    print(f"  {'='*60}")

    state_values = final_state.values
    print(f"\n  📈 总迭代次数: {state_values.get('iteration', 0)}")

    if state_values.get("requirements"):
        print(f"\n  📋 最终需求:")
        print(f"  {state_values['requirements'][:200]}...")

    if state_values.get("code"):
        print(f"\n  💻 最终代码:")
        print(f"  {state_values['code'][:300]}...")

    if state_values.get("test_results"):
        print(f"\n  🧪 最终测试结果:")
        print(f"  {state_values['test_results'][:300]}...")


def demo_stream_messages():
    """演示：流式查看消息流"""
    print_step("流式消息输出（stream_mode='messages'）")

    graph = build_team_graph()
    config = {"configurable": {"thread_id": "msg_stream"}}

    initial_state = {
        "messages": [HumanMessage(content="写一个函数，输入一个列表返回其中所有偶数的平方和")],
        "user_request": "写一个函数，输入一个列表返回其中所有偶数的平方和",
        "requirements": "",
        "code": "",
        "test_results": "",
        "next_agent": "",
        "iteration": 0,
    }

    print(f"\n  📝 需求: 写一个函数，输入一个列表返回其中所有偶数的平方和")
    print(f"\n  🔄 实时消息流:\n")

    # stream_mode="messages" 实时显示 LLM 的 token 流
    # 这需要搭配 stream_mode 参数
    try:
        for msg, metadata in graph.stream(
            initial_state,
            config=config,
            stream_mode="messages",
        ):
            if hasattr(msg, "content") and msg.content:
                content = str(msg.content)
                if len(content) > 0 and len(content) < 500:
                    print(f"  💬 {content[:100]}...")
    except Exception:
        # 如果 messages 模式不支持，回退到 updates 模式
        for event in graph.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, state_update in event.items():
                msgs = state_update.get("messages", [])
                for msg in msgs:
                    if hasattr(msg, "content") and msg.content:
                        print(f"  💬 [{node_name}] {str(msg.content)[:100]}...")


def demo_interactive():
    """交互式多智能体团队"""
    print_step("交互式多智能体团队")

    print("\n  输入 'quit' 退出\n")
    print("  描述你的开发需求，多智能体团队将协作完成：")
    print("  - PM 分析需求 → Dev 生成代码 → Tester 测试验证\n")

    while True:
        request = input("  📝 需求: ").strip()
        if request.lower() in ("quit", "exit"):
            break
        if not request:
            continue

        try:
            run_team(request)
        except Exception as e:
            print(f"\n  ❌ 流程出错: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "─" * 60 + "\n")


def main():
    config = get_llm_config()
    print_separator("P10: 多智能体开发团队")
    print(f"模型: {config.model_name}\n")

    print("  系统架构:")
    print("  START → Supervisor → ┬─ PM子图 → Supervisor → ...")
    print("                       ├─ Dev子图 → Supervisor → ...")
    print("                       ├─ Tester子图 → Supervisor → ...")
    print("                       └─ FINISH → END\n")

    print("  团队成员:")
    print("    🧑‍💼 PM Agent   — 产品经理，分析需求")
    print("    👨‍💻 Dev Agent  — 开发者，生成代码")
    print("    🧪 Tester Agent — 测试员，验证代码\n")

    # 演示 1：自动开发流程
    demo_request = "写一个 Python 函数，输入一个整数列表，返回所有偶数的平方和。要求有 print 输出验证。"
    run_team(demo_request)

    print("\n" + "═" * 60 + "\n")

    # 演示 2：交互式
    demo_interactive()

    print("\n✅ P10 演示完成！恭喜完成全部学习路径！")
    print("\n💡 关键收获：")
    print("   - Supervisor 模式是多智能体编排的核心")
    print("   - 子图让每个智能体可以独立设计和扩展")
    print("   - 流式输出实时展示多智能体协作过程")
    print("   - 整合了 P1-P9 的所有知识点")


if __name__ == "__main__":
    main()
