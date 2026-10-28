"""
Official LangChain ChatModel Factory.

Provides:
- Live `ChatOpenAI` (OpenAI or DeepSeek) with `.bind_tools(tools)` when API keys are configured.
- Concise `MockDeterministicChatModel` implementing `BaseChatModel` & `.bind_tools(tools)` for offline/CI execution.
"""

import os
from typing import Any, List, Optional, Sequence
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI


TOOL_DEFAULT_ARGS = {
    "calculate_demand_forecast_tool": {"sku": "SKU-MED-901", "emergency_shock_factor": 0.80},
    "calculate_inventory_metrics_tool": {"current_stock": 750, "daily_demand": 247.5, "strategic_reserve_floor": 500},
    "query_risk_radar_tool": {"sku": "SKU-MED-901"},
    "evaluate_supplier_proposals_tool": {"quantity_needed": 1549},
    "plan_freight_dispatch_tool": {"quantity_units": 1549, "urgency_level": "CRITICAL", "require_security_escort": True},
}


class MockDeterministicChatModel(BaseChatModel):
    """
    Deterministic ChatModel implementing official LangChain tool-calling interfaces.
    Emits `tool_calls` on initial invocation and terminates cleanly once `ToolMessage` is observed.
    """
    model_name: str = "mock-sovereign-agent-llm"
    bound_tools: List[Any] = []

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "MockDeterministicChatModel":
        return MockDeterministicChatModel(bound_tools=list(tools))

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Once ToolNode has executed and appended a ToolMessage, stop tool-calling and conclude
        if messages and isinstance(messages[-1], ToolMessage):
            ai_msg = AIMessage(content=f"Synthesized tool observation: {messages[-1].content}")
            return ChatResult(generations=[ChatGeneration(message=ai_msg)])

        tool_calls = [
            {
                "name": getattr(t, "name", str(t)),
                "args": TOOL_DEFAULT_ARGS.get(getattr(t, "name", str(t)), {}),
                "id": f"call_{i}",
                "type": "tool_call",
            }
            for i, t in enumerate(self.bound_tools)
            if getattr(t, "name", str(t)) in TOOL_DEFAULT_ARGS
        ]

        ai_msg = AIMessage(
            content="Agent reasoning completed using official LangChain model and tool binding.",
            tool_calls=tool_calls,
        )
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])

    @property
    def _llm_type(self) -> str:
        return "mock_deterministic_llm"


def get_agent_llm(temperature: float = 0.0) -> BaseChatModel:
    """
    Returns an instantiated LangChain ChatModel (DeepSeek, OpenAI, or Mock fallback).
    """
    mode = os.getenv("LLM_MODE", "auto").lower().strip()
    provider = os.getenv("LLM_PROVIDER", "auto").lower().strip()

    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if (provider == "deepseek" or (deepseek_key and provider == "auto")) and mode != "mock":
        if deepseek_key and not deepseek_key.startswith("your_"):
            return ChatOpenAI(
                model=os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat"),
                temperature=temperature,
                api_key=deepseek_key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            )

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and mode != "mock" and not openai_key.startswith("your_"):
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            temperature=temperature,
            api_key=openai_key,
        )

    return MockDeterministicChatModel()
