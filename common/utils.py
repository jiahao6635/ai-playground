"""
utils.py — 通用工具函数

提供跨项目复用的辅助功能。
"""

import sys
import os

# 将项目根目录加入 Python 路径，使所有子项目能 from common.xxx import yyy
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def print_separator(title: str = "", char: str = "=", width: int = 60):
    """打印分隔线，用于美化命令行输出"""
    if title:
        side = (width - len(title) - 2) // 2
        print(f"\n{char * side} {title} {char * side}")
    else:
        print(char * width)


def print_step(step: str, content: str = ""):
    """打印步骤信息"""
    print(f"\n{'─' * 60}")
    print(f"📋 {step}")
    if content:
        print(f"{'─' * 60}")
        print(content)
    print(f"{'─' * 60}")
