"""
Official LangGraph v1.0 ReAct Agent Sub-Graph Factory.

Uses official LangGraph prebuilt primitives:
- `MessagesState` (`Annotated[list[AnyMessage], add_messages]`)
- `ToolNode` (`langgraph.prebuilt.ToolNode`)
- `tools_condition` (`langgraph.prebuilt.tools_condition`)
"""

from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from src.supply_chain.llm import get_agent_llm


def build_react_agent(tools: list):
    """Build a compiled LangGraph ReAct sub-graph using official ToolNode & tools_condition."""
    model = get_agent_llm(temperature=0.0).bind_tools(tools)

    def call_model(state: MessagesState):
        return {"messages": [model.invoke(state["messages"])]}

    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    return workflow.compile()
