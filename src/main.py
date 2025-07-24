from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState

from src.nodes.aggregator import aggregator_node
from src.nodes.resource_monitor import resource_monitor_node
from src.nodes.worker import worker_node
from src.nodes.tester import tester
from src.nodes.manager import manager_node
from src.nodes.manager_planning import manager_planning_node
from src.nodes.retriever import retriever_node

from src.edges.route_after_tester import route_after_tester
from src.edges.route_after_manager import route_after_manager


graph = StateGraph(AgentState)

graph.add_node("manager", manager_node)
graph.add_node("resource_monitor", resource_monitor_node)
graph.add_node("worker", worker_node)
graph.add_node("tester", tester)
graph.add_node("aggregator", aggregator_node)
graph.add_node("manager_planning", manager_planning_node)
graph.add_node("retriever", retriever_node)

graph.add_entry_node("manager")
graph.add_conditional_edges(
    "manager",

)

graph.add_edge("retriever", "manager_planning")
graph.add_edge("manager_planning", "resource_monitor")
graph.add_edge("resource_monitor", "worker") 
graph.add_edge("worker", "aggregator")
graph.add_edge("aggregator", "tester")

graph.add_conditional_edges(
    "tester",
    edges={}
)

graph.compile()
