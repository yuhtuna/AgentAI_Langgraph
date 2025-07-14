# Project Genesis: Low-Code AI Application Platform (LangGraph Edition)
##Important: consider to integrate with narbtech!
## 1. Vision & Mission 🎯

**Vision:** To create a premier low-code/no-code platform that allows anyone—from entrepreneurs to enterprise users—to design, build, and deploy custom business logic as a functional application without writing a single line of code.

**Mission for the Dev Team:** Our mission is to engineer the underlying multi-agent system using **`langgraph`**. We will build an intelligent, graph-based workflow that interprets user requirements and autonomously handles the entire development lifecycle: planning, coding, integration, testing, and deployment.

---

## 2. Core Architecture with `langgraph` 🛠️

The system is architected as a **stateful graph** where each node represents an agent or a specific function. `langgraph` will manage the state and orchestrate the flow of control between these nodes, enabling complex logic like cycles for self-correction.

### **The `AgentState` Definition**

The entire workflow is orchestrated around a central `AgentState` object. This `TypedDict` is passed to each node, ensuring data consistency and allowing any node to access the full context of the job.

```python
from typing import TypedDict, List, Optional, Dict

# A single task for a worker agent
class Task(TypedDict):
    id: int
    role: str
    goal: str
    output_format: str
    result: Optional[str]

# The structured output from the Tester node
class ValidationReport(TypedDict):
    status: str  # "Passed" or "Failed"
    details: str

# The central state graph object
class AgentState(TypedDict):
    user_request: str
    clarified_request: str
    is_clarification_needed: bool
    clarification_questions: List[str]
    
    task_plan: List[Task]
    
    # Using a dict for results allows for aggregation
    completed_tasks: Dict[int, Task]
    
    final_deliverable: str
    validation_report: ValidationReport
    
    cost_estimate: float
    current_cost: float
```

### Recommended Technology Stack
This stack is designed to integrate seamlessly with our langgraph core.

| Component             | Recommendation                 | Rationale                                                                                             |
|-----------------------|--------------------------------|-------------------------------------------------------------------------------------------------------|
| **Backend Language**  | Python                         | Native environment for langgraph and the wider AI ecosystem.                                          |
| **Agent Framework**   | LangGraph                      | Manages the state, control flow, and cyclical logic of our agent team.                                |
| **Web Framework**     | FastAPI                        | High performance, async support, and uses Pydantic for data models, aligning with our AgentState.     |
| **Database (Relational)** | PostgreSQL                   | For robust logging of agent states, tasks, and user sessions.                                         |
| **Database (Vector)** | Qdrant, Pinecone, or ChromaDB  | To give our agents long-term memory and powerful retrieval capabilities.                              |
| **Message Queue**     | Redis               | While langgraph handles the logic flow, a message queue is still recommended for ingesting initial user requests and managing other async background tasks. |
| **Deployment**        | Docker, Kubernetes             | For creating a scalable and maintainable production environment.                                      |

---

## 3. The `langgraph` Graph: Nodes & Edges 📈
Our agent workflow will be implemented as a `StatefulGraph` in `langgraph`. Below are the nodes and the conditional logic that will define our application's "brain."

### Graph Nodes (The AI Team)
Each node is a Python function that takes `AgentState` as input and returns a dictionary to update the state.

- **`manager_clarification_node` (Entry Point):**
  - **Input from State:** `user_request`
  - **Logic:** Calls an LLM to check for ambiguity in the user's prompt.
  - **Output to State:** Updates `is_clarification_needed` and `clarification_questions`.

- **`manager_planning_node`:**
  - **Input from State:** `clarified_request`
  - **Logic:** Uses an LLM with a "project manager" persona to decompose the request into a list of `Task` objects.
  - **Output to State:** Updates `task_plan`.

- **`resource_monitor_node`:**
  - **Input from State:** `task_plan`
  - **Logic:** Analyzes the tasks to generate a `cost_estimate`. Real-time tracking will be handled by decorators on tool functions.
  - **Output to State:** Updates `cost_estimate`.

- **`worker_node`:**
  - **Input from State:** `task_plan`
  - **Logic:** This node will likely use langgraph's dynamic parallelism ("spawning") to execute each task from the `task_plan` concurrently. Each worker calls tools from a `SharedResources` module.
  - **Output to State:** Updates `completed_tasks` with the result of each task.

- **`aggregator_node`:**
  - **Input from State:** `completed_tasks`
  - **Logic:** After all parallel worker branches have finished, this node synthesizes their outputs into a single deliverable.
  - **Output to State:** Updates `final_deliverable`.

- **`tester_node`:**
  - **Input from State:** `final_deliverable`, `clarified_request`
  - **Logic:** Calls an LLM to validate the deliverable against the original request, producing a structured report.
  - **Output to State:** Updates `validation_report`.

### Graph Edges & Conditional Logic
This is where we define the application's flow control using `langgraph`'s edge management.

**Set Entry Point:** The graph will start with the first step of the process.
```python
workflow.set_entry_point("manager_clarification_node")
```

**Clarification Loop (Conditional Edge):** This edge decides whether to proceed with planning or to pause and wait for more user input.
```python
# After manager_clarification_node
workflow.add_conditional_edges(
    "manager_clarification_node",
    lambda state: not state["is_clarification_needed"],
    {
        True: "manager_planning_node",
        False: END # The graph ends, API returns questions to user
    }
)
```

**Main Execution Path (Standard Edges):** The linear flow from planning to testing.
```python
workflow.add_edge('manager_planning_node', 'resource_monitor_node')
workflow.add_edge('resource_monitor_node', 'worker_node')
workflow.add_edge('worker_node', 'aggregator_node')
workflow.add_edge('aggregator_node', 'tester_node')
```

**Self-Correction Loop (Conditional Edge):** The critical feedback loop. Based on the Tester's report, the graph either finishes or re-routes to the planning stage for a second attempt.
```python
# After tester_node
workflow.add_conditional_edges(
    "tester_node",
    lambda state: state["validation_report"]["status"],
    {
        "Passed": END,
        "Failed": "manager_planning_node" # Re-route for revision
    }
)
```
