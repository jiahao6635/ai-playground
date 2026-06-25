"""
checkpointer.py — 持久化配置模块

学习内容：
  1. InMemorySaver — 内存级检查点
  2. SqliteSaver — SQLite 持久化检查点
  3. get_checkpointer() 工厂函数

检查点的作用：
  - 每个节点执行后自动保存状态
  - 程序重启后能恢复之前的对话
  - 通过 thread_id 隔离不同用户的会话

InMemorySaver vs SqliteSaver：
  InMemorySaver: 保存在内存中，程序退出后丢失（适合演示和测试）
  SqliteSaver:   保存在 SQLite 数据库中，程序重启后仍可恢复（适合生产）
"""

import os

from langgraph.checkpoint.memory import InMemorySaver

# SQLite 持久化（可选）
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    _HAS_SQLITE = True
except ImportError:
    _HAS_SQLITE = False

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.db")


def get_checkpointer(use_sqlite: bool = True):
    """
    获取检查点保存器。

    Args:
        use_sqlite: True 使用 SQLite 持久化，False 使用内存

    Returns:
        Checkpointer 实例
    """
    if use_sqlite and _HAS_SQLITE:
        # SqliteSaver.from_conn_string 返回一个上下文管理器
        # 使用 with 语句确保数据库连接正确管理
        return SqliteSaver.from_conn_string(DB_PATH)
    else:
        return InMemorySaver()


def get_memory_saver():
    """
    获取内存检查点保存器（简单版，不需要上下文管理器）。

    适合演示场景，程序重启后数据丢失。
    """
    return InMemorySaver()
