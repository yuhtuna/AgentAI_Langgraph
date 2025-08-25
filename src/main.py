"""
Main LangGraph Workflow with HITL (Human-in-the-Loop) Integration

This module defines the complete LangGraph workflow that orchestrates the development
process. The workflow includes a HITL controller that can automatically pause execution
when human input is needed, enabling collaborative development between AI agents and humans.

Workflow Overview:
1. Manager Node: Analyzes user requests and detects when clarification is needed
2. HITL Controller: Decides whether to pause for human input or continue execution
3. Planning & Execution: Normal development workflow when no pause is needed
4. Testing & Validation: Final validation of completed work

HITL Integration Points:
- Automatic pause when clarification is needed
- Pause for user approval of major plan modifications
- Pause when user interrupts are requested
- Resume execution after receiving human input
"""

from typing import TypedDict, List, Union
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from state import AgentState, ValidationReport, Task

# Import all workflow nodes
from nodes.aggregator import aggregator_node
from nodes.resource_monitor import resource_monitor_node
from nodes.worker import worker_node
from nodes.tester import tester
from nodes.manager import manager_node
from nodes.manager_planning import manager_planning_node
from nodes.retriever import retriever_node
from nodes.hitl_controller import hitl_controller_node

# Import routing logic
from edges.route_after_tester import route_after_tester
from edges.route_after_manager import route_after_manager

# Create the main workflow graph
graph = StateGraph(AgentState)

# Add all workflow nodes
graph.add_node("manager", manager_node)                    # Entry point - analyzes user requests
graph.add_node("hitl_controller", hitl_controller_node)   # HITL checkpoint - manages pauses
graph.add_node("resource_monitor", resource_monitor_node)  # Monitors resource usage
graph.add_node("worker", worker_node)                      # Executes development tasks
graph.add_node("tester", tester)                          # Validates completed work
graph.add_node("aggregator", aggregator_node)             # Combines task results
graph.add_node("manager_planning", manager_planning_node) # Creates detailed task plans
graph.add_node("retriever", retriever_node)               # Retrieves relevant context

# Set the entry point of the workflow
graph.set_entry_point("manager")

# PHASE 1: Request Analysis and HITL Check
# The manager analyzes the user request and the HITL controller decides if a pause is needed
graph.add_edge("manager", "hitl_controller")

# HITL Decision Point: Pause or Continue?
# This is the critical integration point where the system can pause for human input
graph.add_conditional_edges(
    "hitl_controller",
    lambda state: "pause" if state.get("is_paused", False) else "continue",
    {
        "pause": END,        # Pause execution - wait for human input
        "continue": "route_manager"  # Continue with normal development workflow
    }
)

# PHASE 2: Development Workflow Routing
# After HITL check, route to appropriate development phase
graph.add_conditional_edges(
    "route_manager",
    route_after_manager, 
    {
        "clarify": END,      # Pause for user clarification
        "plan": "retriever", # Proceed with planning phase
        "replan": "manager_planning"  # Replan if needed
    }
)

# Add the route_manager node (pass-through node for routing decisions)
graph.add_node("route_manager", lambda state: state)

# PHASE 3: Planning and Context Retrieval
# Retrieve relevant context and create detailed development plan
graph.add_edge("retriever", "manager_planning")

# PHASE 4: Resource Planning and Task Execution
# Monitor resources and execute development tasks
graph.add_edge("manager_planning", "resource_monitor")
graph.add_edge("resource_monitor", "worker") 

# PHASE 5: Result Aggregation and Testing
# Combine completed work and validate the final deliverable
graph.add_edge("worker", "aggregator")

# PHASE 6: Final Validation
# Test the completed work and decide on next steps
graph.add_conditional_edges(
    "tester",
    route_after_tester, 
    {
        "passed": END,           # Work completed successfully
        "failed": "manager_planning"  # Replan if validation failed
    }
)

# Compile the graph into an executable workflow
graph.compile()

# Initialize the workflow with default state
# This state includes all HITL fields initialized to their default values
initial_state = AgentState(
    user_request="[Enter your development request here]",
    clarified_request="",
    is_clarification_needed=False,
    clarification_questions=[],
    retrieved_context=[],
    task_plan=[],
    completed_tasks=[],
    final_deliverable="",
    validation_report=ValidationReport(status="", details=""),
    cost_estimate=0.0,
    current_cost=0.0,
    user_interrupt=None,
    manager_analysis=None,
    # HITL pause mechanism fields - initialized to allow normal execution
    is_paused=False,
    pause_reason="",
    waiting_for_user_input=False,
    user_input_received=None,
    resume_trigger=None
)

# Compile the final executable workflow
compiled_graph = graph.compile()

# Note: The workflow is now ready for use with the HITL system
# To execute it, use one of the following:
# - python hitl_runner.py (interactive mode)
# - python demo_hitl.py (demo scenarios)
# - python custom_test.py (custom testing)
# - Import and use in your own scripts
