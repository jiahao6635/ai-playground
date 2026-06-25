"""
P9: 代码审批系统 — Human-in-the-Loop

学习内容：
  1. interrupt() 暂停图执行等待人工审批
  2. Command.resume() 恢复执行并注入人工决策
  3. 交互式审批流程：生成 → 审查 → 执行/重新生成

流程：
  1. 用户输入代码需求
  2. LLM 生成代码
  3. interrupt() 暂停，展示代码给用户审查
  4. 用户选择：批准 / 拒绝（附反馈）/ 修改代码
  5. Command.resume() 恢复执行
  6. 批准则执行代码，拒绝则重新生成

运行：python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from graph import build_approval_graph


def run_approval_flow(requirement: str):
    """
    运行完整的代码审批流程。

    展示 interrupt/resume 的完整交互：
    1. 启动图 → generate 节点生成代码 → await_review 节点 interrupt 暂停
    2. 检测到暂停，展示代码给用户
    3. 用户审查并做出决策
    4. Command.resume 恢复执行
    5. 如果被拒绝，循环回到步骤 1（重新生成）
    """
    graph = build_approval_graph()
    config = {"configurable": {"thread_id": "approval_session"}}

    # 初始状态
    initial_state = {
        "messages": [],
        "requirement": requirement,
        "generated_code": "",
        "review_status": "pending",
        "human_feedback": "",
        "modified_code": "",
        "execution_result": "",
        "iteration": 0,
    }

    # ──────────────────────────────────────────────
    # 第一次调用：开始生成代码
    # 图会在 await_review 节点 interrupt() 处暂停
    # ──────────────────────────────────────────────
    print(f"\n  📝 需求: {requirement}")
    print(f"  🚀 启动审批流程...\n")

    result = graph.invoke(initial_state, config=config)

    # ──────────────────────────────────────────────
    # 检查是否在 interrupt 处暂停
    # 当图遇到 interrupt() 时，invoke 返回时状态中会包含暂停信息
    # 我们可以通过检查 result 中是否有 execution_result 来判断是否完成
    # ──────────────────────────────────────────────
    max_iterations = 5
    current_iteration = 0

    while current_iteration < max_iterations:
        current_iteration += 1

        # 获取当前状态
        state = graph.get_state(config)

        # 检查图是否已完成
        if state.next == ():
            # 图已完成
            break

        # 检查是否在 await_review 处暂停
        if "await_review" in state.next:
            # 获取 interrupt 传递的值（生成的代码）
            # 暂停时，state.values 包含 generate 节点的输出
            generated_code = state.values.get("generated_code", "")
            iteration = state.values.get("iteration", 1)

            # ──────────────────────────────────────────────
            # 展示代码给用户审查
            # ──────────────────────────────────────────────
            print(f"\n  {'─'*60}")
            print(f"  📋 第 {iteration} 版代码（等待审批）:")
            print(f"  {'─'*60}")
            print(f"\n{generated_code}\n")
            print(f"  {'─'*60}")
            print(f"  审查选项:")
            print(f"    1. 批准并执行")
            print(f"    2. 拒绝（附反馈，重新生成）")
            print(f"    3. 修改代码后执行")
            print(f"    4. 退出")
            print(f"  {'─'*60}")

            choice = input("\n  选择 [1-4]: ").strip()

            if choice == "1":
                # 批准
                print("\n  ✅ 已批准，开始执行...")
                resume_value = Command(resume={"action": "approve", "feedback": "", "code": ""})
                result = graph.invoke(resume_value, config=config)

            elif choice == "2":
                # 拒绝并附反馈
                feedback = input("  📝 请输入反馈意见: ").strip()
                print(f"\n  ❌ 已拒绝，将根据反馈重新生成...")
                resume_value = Command(resume={
                    "action": "reject",
                    "feedback": feedback,
                    "code": "",
                })
                result = graph.invoke(resume_value, config=config)

            elif choice == "3":
                # 修改代码
                print("\n  ✏️ 请输入修改后的代码（输入空行结束）：")
                lines = []
                while True:
                    line = input()
                    if line == "":
                        break
                    lines.append(line)
                modified_code = "\n".join(lines)

                print("\n  ✅ 代码已修改，开始执行...")
                resume_value = Command(resume={
                    "action": "modify",
                    "feedback": "用户修改了代码",
                    "code": modified_code,
                })
                result = graph.invoke(resume_value, config=config)

            elif choice == "4":
                print("\n  👋 已退出审批流程。")
                return

            else:
                print("\n  ⚠️ 无效选择，请重试。")
                continue

        else:
            break

    # 展示最终结果
    final_state = graph.get_state(config)
    execution_result = final_state.values.get("execution_result", "")

    print(f"\n  {'='*60}")
    print(f"  📊 审批流程完成")
    print(f"  {'='*60}")

    if execution_result:
        print(f"\n  🔧 执行结果:")
        print(f"  {execution_result}")
    else:
        print(f"\n  ⚠️ 流程未完成或代码未执行。")

    # 打印迭代历史
    iteration = final_state.values.get("iteration", 0)
    status = final_state.values.get("review_status", "unknown")
    print(f"\n  📈 总迭代次数: {iteration}")
    print(f"  📌 最终状态: {status}")


def main():
    config = get_llm_config()
    print_separator("P9: 代码审批系统（Human-in-the-Loop）")
    print(f"模型: {config.model_name}\n")

    print("  工作流图:")
    print("  START → 生成代码 → 等待审批(interrupt) → ┬─ 批准 → 执行 → END")
    print("                                           ├─ 拒绝 → 重新生成 → ...")
    print("                                           └─ 修改 → 执行 → END\n")

    print("  输入 'quit' 退出\n")

    while True:
        requirement = input("  📝 请描述代码需求: ").strip()
        if requirement.lower() in ("quit", "exit"):
            break
        if not requirement:
            continue

        try:
            run_approval_flow(requirement)
        except Exception as e:
            print(f"\n  ❌ 流程出错: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "─" * 60 + "\n")

    print("\n✅ P9 演示完成！")
    print("\n💡 关键收获：")
    print("   - interrupt() 让图能在任意节点暂停等待人工输入")
    print("   - Command.resume() 注入人工决策并恢复执行")
    print("   - 检查点是 interrupt/resume 的基础")
    print("   - 人机协作让 AI 在关键决策点有人工把关")


if __name__ == "__main__":
    main()
