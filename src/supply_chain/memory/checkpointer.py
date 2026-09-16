"""
State Persistence and Checkpointing Factory for LangGraph.

Supports:
1. MemorySaver: In-memory checkpointing (fast, zero external dependencies, ideal for tests & dev).
2. SqliteSaver: Disk-backed SQLite checkpointing for enterprise audit trails and crash recovery.
"""

import os
from typing import Optional, Union
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer(
    backend: Optional[str] = None,
    sqlite_path: Optional[str] = None,
) -> BaseCheckpointSaver:
    """
    Factory function returning the appropriate LangGraph checkpointer.

    Args:
        backend: "memory", "sqlite", or "auto" (reads from CHECKPOINTER_BACKEND env var).
        sqlite_path: Filepath for the SQLite database (defaults to 'reports/checkpoints.db').

    Returns:
        BaseCheckpointSaver: Configured LangGraph checkpointer instance.
    """
    selected_backend = (backend or os.getenv("CHECKPOINTER_BACKEND", "memory")).lower().strip()

    if selected_backend == "sqlite":
        db_path = sqlite_path or os.getenv("SQLITE_CHECKPOINT_PATH", "reports/checkpoints.db")
        # Ensure target directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        try:
            # LangGraph SQLite checkpoint saver
            from langgraph.checkpoint.sqlite import SqliteSaver
            import sqlite3

            conn = sqlite3.connect(db_path, check_same_thread=False)
            return SqliteSaver(conn)
        except ImportError:
            # Fallback to MemorySaver if sqlite extra is not installed
            print(
                f"[WARNING] 'langgraph.checkpoint.sqlite' not found. "
                f"Falling back to in-memory MemorySaver. "
                f"Install 'langgraph-checkpoint-sqlite' to enable disk-backed checkpoints."
            )
            return MemorySaver()

    # Default: In-memory checkpointer
    return MemorySaver()


def get_default_checkpointer() -> BaseCheckpointSaver:
    """Convenience shortcut returning the default configured checkpointer."""
    return get_checkpointer()
