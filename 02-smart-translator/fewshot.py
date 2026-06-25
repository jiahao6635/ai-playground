"""
P2: 智能翻译器 — Few-shot 提示

学习内容：
  1. FewShotChatMessagePromptTemplate 构建 Few-shot 聊天提示
  2. 通过示例引导 LLM 学习翻译风格和术语处理
  3. Few-shot vs Zero-shot 的效果差异

Few-shot 原理：
  在提示词中提供几个"输入→输出"示例，
  LLM 会从示例中学习模式，按照相同的风格和格式生成。
  适合需要特定风格、术语一致、或格式特殊的场景。

运行：python fewshot.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser


def demo_fewshot():
    """演示 Few-shot 提示：专业术语翻译"""
    print_step("Few-shot 提示：专业 IT 术语翻译")

    llm = get_llm(temperature=0.2)

    # ──────────────────────────────────────────────
    # 1. 定义 Few-shot 示例
    # 每个示例是 {"input": ..., "output": ...} 字典
    # 这些示例教会 LLM：
    #   - 将 IT 术语翻译为中文行业标准译法
    #   - 在括号中附注英文原文
    #   - 保持简洁
    # ──────────────────────────────────────────────
    examples = [
        {
            "input": "The API endpoint returns a JSON response.",
            "output": "API 端点（endpoint）返回 JSON 格式的响应。",
        },
        {
            "input": "Deploy the microservices to the Kubernetes cluster.",
            "output": "将微服务（microservices）部署到 Kubernetes 集群（cluster）中。",
        },
        {
            "input": "The middleware intercepts HTTP requests for authentication.",
            "output": "中间件（middleware）拦截 HTTP 请求以进行身份认证（authentication）。",
        },
    ]

    # ──────────────────────────────────────────────
    # 2. 构建示例的提示模板
    # 每个 example 按此模板格式化为一条 human + 一条 ai 消息
    # ──────────────────────────────────────────────
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{output}"),
    ])

    # ──────────────────────────────────────────────
    # 3. 构建 Few-shot 模板
    # FewShotChatMessagePromptTemplate 会将所有示例展开为消息序列
    # ──────────────────────────────────────────────
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    # ──────────────────────────────────────────────
    # 4. 构建完整提示：system + few-shot 示例 + 用户输入
    # ──────────────────────────────────────────────
    final_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个专业的 IT 技术文档翻译。"
            "将英文技术文本翻译为中文，"
            "专业术语在括号中附注英文原文，"
            "保持技术准确性和语言自然。"
        )),
        # Few-shot 示例会在这里展开为多条 human/ai 消息
        few_shot_prompt,
        # 用户的实际输入
        ("human", "{input}"),
    ])

    # 构建链
    chain = final_prompt | llm | StrOutputParser()

    # 测试：LLM 会按照示例的风格翻译
    test_cases = [
        "The container orchestrator scales pods based on CPU utilization.",
        "The CI/CD pipeline triggers a rolling update on the container registry.",
        "The RESTful API uses OAuth 2.0 for token-based authorization.",
    ]

    for test in test_cases:
        result = chain.invoke({"input": test})
        print(f"\n  EN: {test}")
        print(f"  CN: {result}")

    print("\n  💡 注意：LLM 学会了在括号中附注英文术语的风格，")
    print("     这正是 Few-shot 示例引导的效果。")


def demo_zero_vs_fewshot():
    """对比 Zero-shot vs Few-shot"""
    print_step("对比：Zero-shot vs Few-shot")

    llm = get_llm(temperature=0.2)

    test_text = "The message broker publishes events to the event-driven architecture."

    # Zero-shot：只有 system + human，没有示例
    zero_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的 IT 技术文档翻译。将英文技术文本翻译为中文。"),
        ("human", "{input}"),
    ])
    zero_chain = zero_prompt | llm | StrOutputParser()
    zero_result = zero_chain.invoke({"input": test_text})

    # Few-shot：有示例引导
    examples = [
        {
            "input": "The API endpoint returns a JSON response.",
            "output": "API 端点（endpoint）返回 JSON 格式的响应。",
        },
        {
            "input": "Deploy the microservices to the Kubernetes cluster.",
            "output": "将微服务（microservices）部署到 Kubernetes 集群（cluster）中。",
        },
    ]
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{output}"),
    ])
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )
    few_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的 IT 技术文档翻译。专业术语在括号中附注英文原文。"),
        few_shot_prompt,
        ("human", "{input}"),
    ])
    few_chain = few_prompt | llm | StrOutputParser()
    few_result = few_chain.invoke({"input": test_text})

    print(f"\n  原文: {test_text}")
    print(f"\n  Zero-shot: {zero_result}")
    print(f"  Few-shot:  {few_result}")
    print("\n  💡 Few-shot 通过示例更精确地控制了翻译风格和术语处理。")


def main():
    config = get_llm_config()
    print_separator("P2: Few-shot 提示演示")
    print(f"模型: {config.model_name}\n")

    demo_fewshot()
    demo_zero_vs_fewshot()

    print("\n✅ Few-shot 演示完成！")


if __name__ == "__main__":
    main()
