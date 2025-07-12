import pytest
from unittest.mock import patch, MagicMock

from langgraph_project.graph import create_workflow
from langgraph_project.state import AgentState


def test_workflow_creation():
    """Test that the workflow can be created and compiled."""
    app = create_workflow()
    assert app is not None


@patch('langgraph_project.llm_config.llm')
def test_planner_node(mock_llm):
    """Test the planner node functionality."""
    from langgraph_project.nodes.example_node import planner_node
    
    # Mock the LLM response
    mock_response = MagicMock()
    mock_response.content = "Test plan content"
    mock_llm.invoke.return_value = mock_response
    
    # Test state
    state = {"task": "Test task"}
    
    # Call the node
    result = planner_node(state)
    
    # Assertions
    assert "plan" in result
    assert result["plan"] == "Test plan content"
    mock_llm.invoke.assert_called_once()


@patch('langgraph_project.llm_config.llm')
def test_researcher_node(mock_llm):
    """Test the researcher node functionality."""
    from langgraph_project.nodes.example_node import researcher_node
    
    # Mock the LLM response
    mock_response = MagicMock()
    mock_response.content = "Test research content"
    mock_llm.invoke.return_value = mock_response
    
    # Test state
    state = {"plan": "Test plan"}
    
    # Call the node
    result = researcher_node(state)
    
    # Assertions
    assert "draft" in result
    assert result["draft"] == "Test research content"
    mock_llm.invoke.assert_called_once()


@patch('langgraph_project.llm_config.llm')
def test_writer_node(mock_llm):
    """Test the writer node functionality."""
    from langgraph_project.nodes.example_node import writer_node
    
    # Mock the LLM response
    mock_response = MagicMock()
    mock_response.content = "Test final report"
    mock_llm.invoke.return_value = mock_response
    
    # Test state
    state = {"draft": "Test draft"}
    
    # Call the node
    result = writer_node(state)
    
    # Assertions
    assert "review" in result
    assert result["review"] == "Test final report"
    mock_llm.invoke.assert_called_once()
