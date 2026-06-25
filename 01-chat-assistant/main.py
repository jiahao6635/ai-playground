"""
P1: LLM 对话助手 — 基础对话

学习内容：
  1. 从公共模块获取 LLM 实例（get_llm）
  2. 构造消息列表（SystemMessage + HumanMessage）
  3. 调用 invoke() 获取回复
  4. 维护消息历史实现多轮对话

运行：python main.py
"""

import sys
import os

# 确保能导入 common 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.config import get_llm_config
from common.utils import print_separator, print_step

# LangChain 消息类型
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


def main():
    # ──────────────────────────────────────────────
    # 1. 初始化 LLM
    # ──────────────────────────────────────────────
    config = get_llm_config()
    print_separator("P1: LLM 对话助手")
    print(f"模型: {config.model_name}")
    print(f"端点: {config.base_url}")
    print(f"\n输入 'quit' 或 'exit' 退出，输入 'clear' 清空对话历史\n")

    llm = get_llm(temperature=0.7)

    # ──────────────────────────────────────────────
    # 2. 初始化消息历史
    # ──────────────────────────────────────────────
    # SystemMessage 设定 AI 的人设和行为规则
    # 这个消息会一直保留在历史中，影响每次回复
    messages = [
        SystemMessage(content="你是一个友好的中文 AI 助手。请用简洁、清晰的中文回答问题。"),
    ]

    # ──────────────────────────────────────────────
    # 3. 对话循环
    # ──────────────────────────────────────────────
    while True:
        # 接收用户输入
        user_input = input("\n🧑 你: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("👋 再见！")
            break
        if user_input.lower() == "clear":
            # 清空历史，只保留 system 消息
            messages = [messages[0]]
            print("🔄 对话历史已清空")
            continue

        # 将用户输入加入消息历史
        messages.append(HumanMessage(content=user_input))

        # 调用 LLM（传入完整消息历史，实现多轮对话）
        # invoke() 会等待完整回复后一次性返回
        print_step("LLM 思考中...")
        response = llm.invoke(messages)

        # 获取 AI 回复内容
        ai_reply = response.content
        print(f"\n🤖 AI: {ai_reply}")

        # 将 AI 回复也加入历史，这样下一轮对话能记住上下文
        messages.append(AIMessage(content=ai_reply))

        # 显示当前消息历史长度
        print(f"\n   📝 消息历史: {len(messages)} 条")


if __name__ == "__main__":
    main()
