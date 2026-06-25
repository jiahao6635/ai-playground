"""
P1: LLM 对话助手 — 流式输出

学习内容：
  1. llm.stream() vs llm.invoke() 的区别
  2. 流式输出：逐 token 返回，实现打字机效果
  3. 流式输出在用户体验上的优势

对比：
  invoke() — 等待完整回复后一次性返回（适合需要完整结果的场景）
  stream() — 逐 token 返回迭代器（适合聊天界面，实时反馈）

运行：python streaming.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.config import get_llm_config
from common.utils import print_separator, print_step

from langchain_core.messages import SystemMessage, HumanMessage


def demo_invoke():
    """演示 invoke()：一次性返回"""
    print_step("方式一：invoke()（一次性返回完整结果）")

    llm = get_llm(temperature=0.7)
    messages = [
        SystemMessage(content="你是一个中文诗人。"),
        HumanMessage(content="用三句话描述春天。"),
    ]

    start = time.time()
    response = llm.invoke(messages)
    elapsed = time.time() - start

    print(f"\n等待 {elapsed:.2f} 秒后一次性收到完整回复：\n")
    print(f"🤖 {response.content}")
    print(f"\n⏱️ 总耗时: {elapsed:.2f}s")


def demo_stream():
    """演示 stream()：逐 token 返回"""
    print_step("方式二：stream()（流式逐 token 返回）")

    llm = get_llm(temperature=0.7)
    messages = [
        SystemMessage(content="你是一个中文诗人。"),
        HumanMessage(content="用三句话描述秋天。"),
    ]

    print("\n逐 token 流式输出：\n")
    print("🤖 ", end="", flush=True)

    start = time.time()
    full_text = ""

    # stream() 返回一个迭代器，每次 yield 一个 AIMessageChunk
    # AIMessageChunk 包含一小段文本（一个或几个 token）
    for chunk in llm.stream(messages):
        # chunk.content 是当前 token 的文本
        text = chunk.content
        if text:
            print(text, end="", flush=True)  # flush=True 确保立即显示
            full_text += text

    elapsed = time.time() - start
    print(f"\n\n⏱️ 总耗时: {elapsed:.2f}s")
    print(f"📊 收到 {len(full_text)} 个字符")

    print("\n💡 对比：stream() 让用户在第一个 token 产出时就看到输出，")
    print("   而 invoke() 需要等待全部生成完毕。在聊天场景中，stream() 体验更好。")


def demo_stream_comparison():
    """对比 invoke 和 stream 的首字延迟"""
    print_step("首字延迟对比")

    llm = get_llm(temperature=0)
    messages = [
        SystemMessage(content="回答简短。"),
        HumanMessage(content="1+1=?"),
    ]

    # invoke 首字延迟 = 总耗时
    start = time.time()
    llm.invoke(messages)
    invoke_time = time.time() - start

    # stream 首字延迟 = 第一个 token 到达时间
    start = time.time()
    first_token_time = None
    for chunk in llm.stream(messages):
        if chunk.content:
            first_token_time = time.time() - start
            break  # 只测第一个 token

    print(f"\n  invoke() 总耗时:   {invoke_time:.2f}s")
    print(f"  stream() 首字延迟: {first_token_time:.2f}s")
    print(f"\n  💡 stream() 让用户等待时间减少了约 "
          f"{(1 - first_token_time / invoke_time) * 100:.0f}%")


def main():
    config = get_llm_config()
    print_separator("P1: 流式输出演示")
    print(f"模型: {config.model_name}\n")

    demo_invoke()
    demo_stream()
    demo_stream_comparison()

    print("\n✅ 流式输出演示完成！")


if __name__ == "__main__":
    main()
