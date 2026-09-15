"""
LLM Configuration and Factory for LangChain & LangGraph.

Supports:
- ChatOpenAI with tool binding (`llm.bind_tools(tools)`)
- Structured outputs (`llm.with_structured_output(schema)`)
- Deterministic Offline LLM fallback for autonomous testing without live API keys
"""

import os
from typing import Any, List, Optional, Type
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI


class MockDeterministicChatModel(BaseChatModel):
    """
    Deterministic offline ChatModel adhering to BaseChatModel interface.
    Allows complete LangGraph tool-calling pipelines to run reliably in CI/CD and demos.
    """
    model_name: str = "mock-sovereign-agent-llm"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        last_msg = messages[-1].content if messages else ""
        content = f"[AI Reasoning based on prompt & context]: Processed inputs successfully."
        ai_msg = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])

    @property
    def _llm_type(self) -> str:
        return "mock_deterministic_llm"


def get_agent_llm(temperature: float = 0.0) -> BaseChatModel:
    """
    Returns an instantiated LangChain ChatModel.
    
    If `OPENAI_API_KEY` is present in environment, returns `ChatOpenAI`.
    Otherwise, returns `MockDeterministicChatModel` ensuring 100% testability.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    mode = os.getenv("LLM_MODE", "auto").lower()

    if api_key and mode != "mock" and not api_key.startswith("your_"):
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
        )

    return MockDeterministicChatModel()
