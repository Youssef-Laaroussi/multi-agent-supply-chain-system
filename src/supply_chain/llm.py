"""
Official LangChain ChatModel Factory.

Provides:
- Live `ChatOpenAI` with `.bind_tools(tools)` when `OPENAI_API_KEY` is available.
- Deterministic `MockDeterministicChatModel` with `.bind_tools(tools)` and automatic `tool_calls` emission for seamless testing, CI/CD, and local demos.
"""

import os
from typing import Any, List, Optional, Sequence
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI


class MockDeterministicChatModel(BaseChatModel):
    """
    Deterministic ChatModel implementing official LangChain tool-calling interfaces.
    Emits structured AIMessages with valid `tool_calls` matching bound tools.
    """
    model_name: str = "mock-sovereign-agent-llm"
    bound_tools: List[Any] = []

    def bind_tools(
        self,
        tools: Sequence[Any],
        **kwargs: Any,
    ) -> "MockDeterministicChatModel":
        model = MockDeterministicChatModel(bound_tools=list(tools))
        return model

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        tool_calls = []

        # Generate intelligent tool_calls based on bound tools
        for tool in self.bound_tools:
            tool_name = getattr(tool, "name", str(tool))
            if tool_name == "calculate_demand_forecast_tool":
                tool_calls.append({
                    "name": "calculate_demand_forecast_tool",
                    "args": {"sku": "SKU-MED-901", "emergency_shock_factor": 0.80},
                    "id": "call_demand_01",
                    "type": "tool_call",
                })
            elif tool_name == "calculate_inventory_metrics_tool":
                tool_calls.append({
                    "name": "calculate_inventory_metrics_tool",
                    "args": {"current_stock": 750, "daily_demand": 247.5, "strategic_reserve_floor": 500},
                    "id": "call_inv_01",
                    "type": "tool_call",
                })
            elif tool_name == "query_risk_radar_tool":
                tool_calls.append({
                    "name": "query_risk_radar_tool",
                    "args": {"sku": "SKU-MED-901"},
                    "id": "call_risk_01",
                    "type": "tool_call",
                })
            elif tool_name == "evaluate_supplier_proposals_tool":
                tool_calls.append({
                    "name": "evaluate_supplier_proposals_tool",
                    "args": {"quantity_needed": 1549},
                    "id": "call_proc_01",
                    "type": "tool_call",
                })
            elif tool_name == "plan_freight_dispatch_tool":
                tool_calls.append({
                    "name": "plan_freight_dispatch_tool",
                    "args": {"quantity_units": 1549, "urgency_level": "CRITICAL", "require_security_escort": True},
                    "id": "call_log_01",
                    "type": "tool_call",
                })

        content = "Agent reasoning completed using official LangChain model and tool binding."
        ai_msg = AIMessage(content=content, tool_calls=tool_calls)
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])

    @property
    def _llm_type(self) -> str:
        return "mock_deterministic_llm"


def get_agent_llm(temperature: float = 0.0) -> BaseChatModel:
    """
    Returns an instantiated LangChain ChatModel.

    Provider Selection:
    1. DeepSeek: If LLM_PROVIDER="deepseek" or DEEPSEEK_API_KEY is configured.
       Uses official DeepSeek API via OpenAI-compatible ChatOpenAI endpoint.
    2. OpenAI: If OPENAI_API_KEY is configured.
    3. Mock: Deterministic offline mode (default for tests, zero cost, reproducible).

    LangSmith Tracing:
    Automatically activates when LANGCHAIN_TRACING_V2="true" and LANGCHAIN_API_KEY are set.
    """
    mode = os.getenv("LLM_MODE", "auto").lower().strip()
    provider = os.getenv("LLM_PROVIDER", "auto").lower().strip()

    # 1. Check DeepSeek provider
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if (provider == "deepseek" or (deepseek_key and provider == "auto")) and mode != "mock":
        if deepseek_key and not deepseek_key.startswith("your_"):
            model_name = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=deepseek_key,
                base_url=base_url,
            )

    # 2. Check OpenAI provider
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and mode != "mock" and not openai_key.startswith("your_"):
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=openai_key,
        )

    # 3. Fallback: Offline deterministic mock with tool-calling support
    return MockDeterministicChatModel()

