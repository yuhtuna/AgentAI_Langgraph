# AgentAI LangGraph Project

This repository contains a LangGraph-based AI agent system with planner, researcher, and writer nodes.

## Project Structure
```
AgentAI/
├── .env                    # Environment variables (add your GOOGLE_API_KEY)
├── .gitignore
├── README.md
├── requirements.txt
├── langgraph_project/
│   ├── __init__.py
│   ├── state.py           # AgentState definition
│   ├── llm_config.py      # LLM configuration
│   ├── graph.py           # Workflow creation
│   ├── main.py            # Main execution
│   ├── nodes/
│   │   ├── __init__.py
│   │   └── example_node.py # Planner, researcher, writer nodes
│   └── edges/
│       ├── __init__.py
│       └── example_edge.py
├── tests/
│   ├── __init__.py
│   └── test_graph.py      # Unit tests
└── .venv/ (virtual environment)
```

## Setup
1. Create virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Configure environment:
   - Copy `.env` and add your `GOOGLE_API_KEY`
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. Run the project:
```powershell
python -m langgraph_project.main
```

5. Run tests:
```powershell
pytest
```

## Features
- **Planner Node**: Creates step-by-step plans for tasks
- **Researcher Node**: Conducts research based on the plan
- **Writer Node**: Writes polished final reports
- **LangGraph Workflow**: Orchestrates the multi-agent system
