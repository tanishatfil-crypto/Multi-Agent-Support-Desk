
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import SupportState
from src.agents import (
    router_node,
    billing_agent_node,
    tech_agent_node,
    general_agent_node
)

def build_support_graph():
    builder = StateGraph(SupportState)

    # Nodes add karo
    builder.add_node("router", router_node)
    builder.add_node("billing_agent", billing_agent_node)
    builder.add_node("tech_agent", tech_agent_node)
    builder.add_node("general_agent", general_agent_node)

    # Entry point
    builder.set_entry_point("router")

    # Conditional routing logic
    def route_decision(state: SupportState):
        cat = state.get("category", "general")
        if cat == "billing":
            return "billing_agent"
        elif cat == "tech":
            return "tech_agent"
        else:
            return "general_agent"

    builder.add_conditional_edges(
        "router",
        route_decision,
        {
            "billing_agent": "billing_agent",
            "tech_agent": "tech_agent",
            "general_agent": "general_agent"
        }
    )

    builder.add_edge("billing_agent", END)
    builder.add_edge("tech_agent", END)
    builder.add_edge("general_agent", END)

    # Memory Checkpointer attach kar rahe hain
    memory = MemorySaver()
    
    # Human-in-the-loop: Interrupt before execution completes if approval needed
    return builder.compile(
        checkpointer=memory,
        interrupt_before=["billing_agent"]  # HITL Approval workflow target
    )