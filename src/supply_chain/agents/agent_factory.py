import json
from typing import Annotated, Literal
from typing_extensions import TypedDict
import operator
from langchain_core.messages import AnyMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from src.supply_chain.llm import get_agent_llm

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def build_react_agent(tools: list):
    """
    Builds a standard LangGraph ReAct Agent sub-graph (llm -> tools loop).
    """
    model = get_agent_llm(temperature=0.0).bind_tools(tools)
    tools_by_name = {tool.name: tool for tool in tools}

    def llm_call(state: MessagesState):
        return {"messages": [model.invoke(state["messages"])]}

    def tool_node(state: MessagesState):
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            # Invoke the tool
            try:
                observation = tool.invoke(tool_call["args"])
                content = json.dumps(observation) if isinstance(observation, dict) else str(observation)
            except Exception as e:
                content = f"Error executing tool: {e}"
            
            result.append(ToolMessage(
                content=content,
                name=tool_call["name"],
                tool_call_id=tool_call["id"]
            ))
        return {"messages": result}

    def should_continue(state: MessagesState) -> Literal["tool_node", END]:
        if state["messages"][-1].tool_calls:
            return "tool_node"
        return END

    workflow = StateGraph(MessagesState)
    workflow.add_node("llm_call", llm_call)
    workflow.add_node("tool_node", tool_node)

    workflow.add_edge(START, "llm_call")
    workflow.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    workflow.add_edge("tool_node", "llm_call")

    return workflow.compile()
