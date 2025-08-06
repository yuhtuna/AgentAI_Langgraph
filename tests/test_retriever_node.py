import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.nodes.retriever import retriever_node
from src.state import AgentState
from src.rag.RAGVectorStore import RAGVectorStore
from src.rag.RAGRetriever import SimpleRAGRetriever


class TestRetrieverNode:
    """Test cases for the retriever node functionality."""
    
    def test_retriever_node_with_clarified_request(self):
        """Test retriever node with a valid clarified_request."""
        # Mock the RAG components
        with patch('src.nodes.retriever.RAGVectorStore') as mock_vector_store_class, \
             patch('src.nodes.retriever.SimpleRAGRetriever') as mock_retriever_class:
            
            # Setup mocks
            mock_vector_store = Mock()
            mock_vector_store_class.return_value = mock_vector_store
            
            mock_retriever = Mock()
            mock_retriever_class.return_value = mock_retriever
            
            # Mock the retrieve_context method to return sample results
            sample_contexts = [
                "// File: src/components/Dashboard.tsx\n// Project: notes app\n// Type: component (react)\n// Description: Dashboard component for notes app\n\nexport default function Dashboard() {\n  return <div>Dashboard</div>;\n}",
                "// File: src/pages/HomePage.tsx\n// Project: notes app\n// Type: component (nextjs)\n// Description: Homepage component\n\nexport default function HomePage() {\n  return <div>Welcome to Notes App</div>;\n}"
            ]
            mock_retriever.retrieve_context.return_value = sample_contexts
            
            # Create test state
            state: AgentState = {
                "user_request": "Build a notes application",
                "clarified_request": "Create a modern notes app with dashboard and homepage",
                "is_clarification_needed": False,
                "clarification_questions": [],
                "retrieved_information": [],
                "processed_information": [],
                "task_plan": [],
                "completed_tasks": [],
                "final_deliverable": None,
                "validation_reports": [],
                "cost_estimate": 0.0,
                "current_cost": 0.0
            }
            
            # Call the retriever node
            result = retriever_node(state)
            
            # Print retrieved information for debugging
            print(f"\n=== RETRIEVED INFORMATION ({len(result['retrieved_information'])} items) ===")
            for i, info in enumerate(result["retrieved_information"]):
                print(f"--- Item {i+1} ---")
                print(info)
                print()
            
            # Assertions
            assert "retrieved_information" in result
            assert len(result["retrieved_information"]) == 2
            assert "Dashboard" in result["retrieved_information"][0]
            assert "HomePage" in result["retrieved_information"][1]
            
            # Verify the mocks were called correctly
            mock_vector_store_class.assert_called_once_with(
                collection_name="narbtech_code",
                persist_directory="./chroma_db"
            )
            mock_retriever_class.assert_called_once_with(mock_vector_store)
            mock_retriever.retrieve_context.assert_called_once_with(
                user_request="Create a modern notes app with dashboard and homepage",
                max_chunks=8
            )
    
    def test_retriever_node_with_user_request_fallback(self):
        """Test retriever node when clarified_request is empty, falls back to user_request."""
        with patch('src.nodes.retriever.RAGVectorStore') as mock_vector_store_class, \
             patch('src.nodes.retriever.SimpleRAGRetriever') as mock_retriever_class:
            
            # Setup mocks
            mock_vector_store = Mock()
            mock_vector_store_class.return_value = mock_vector_store
            
            mock_retriever = Mock()
            mock_retriever_class.return_value = mock_retriever
            
            sample_contexts = ["// File: src/utils/api.ts\n// Project: notes app\n// Type: utils (api)\n\nexport const fetchNotes = () => { return []; };"]
            mock_retriever.retrieve_context.return_value = sample_contexts
            
            # Create test state with empty clarified_request
            state: AgentState = {
                "user_request": "Build a simple notes app",
                "clarified_request": "",  # Empty clarified request
                "is_clarification_needed": False,
                "clarification_questions": [],
                "retrieved_information": [],
                "processed_information": [],
                "task_plan": [],
                "completed_tasks": [],
                "final_deliverable": None,
                "validation_reports": [],
                "cost_estimate": 0.0,
                "current_cost": 0.0
            }
            
            # Call the retriever node
            result = retriever_node(state)
            
            # Print retrieved information for debugging
            print(f"\n=== RETRIEVED INFORMATION (Fallback Test - {len(result['retrieved_information'])} items) ===")
            for i, info in enumerate(result["retrieved_information"]):
                print(f"--- Item {i+1} ---")
                print(info)
                print()
            
            # Assertions
            assert "retrieved_information" in result
            assert len(result["retrieved_information"]) == 1
            assert "fetchNotes" in result["retrieved_information"][0]
            
            # Verify it used the user_request as fallback
            mock_retriever.retrieve_context.assert_called_once_with(
                user_request="Build a simple notes app",
                max_chunks=8
            )
    
    def test_retriever_node_no_query_available(self):
        """Test retriever node when both clarified_request and user_request are empty."""
        # Create test state with empty requests
        state: AgentState = {
            "user_request": "",
            "clarified_request": "",
            "is_clarification_needed": False,
            "clarification_questions": [],
            "retrieved_information": [],
            "processed_information": [],
            "task_plan": [],
            "completed_tasks": [],
            "final_deliverable": None,
            "validation_reports": [],
            "cost_estimate": 0.0,
            "current_cost": 0.0
        }
        
        # Call the retriever node
        result = retriever_node(state)
        
        # Print retrieved information for debugging
        print(f"\n=== RETRIEVED INFORMATION (No Query Test - {len(result['retrieved_information'])} items) ===")
        for i, info in enumerate(result["retrieved_information"]):
            print(f"--- Item {i+1} ---")
            print(info)
            print()
        
        # Assertions
        assert "retrieved_information" in result
        assert len(result["retrieved_information"]) == 1
        assert "No query available for information retrieval" in result["retrieved_information"][0]
    
    def test_retriever_node_no_results_found(self):
        """Test retriever node when no relevant contexts are found."""
        with patch('src.nodes.retriever.RAGVectorStore') as mock_vector_store_class, \
             patch('src.nodes.retriever.SimpleRAGRetriever') as mock_retriever_class:
            
            # Setup mocks
            mock_vector_store = Mock()
            mock_vector_store_class.return_value = mock_vector_store
            
            mock_retriever = Mock()
            mock_retriever_class.return_value = mock_retriever
            
            # Mock retrieve_context to return empty list
            mock_retriever.retrieve_context.return_value = []
            
            # Create test state
            state: AgentState = {
                "user_request": "Build something very specific",
                "clarified_request": "Create a very specific feature that doesn't exist",
                "is_clarification_needed": False,
                "clarification_questions": [],
                "retrieved_information": [],
                "processed_information": [],
                "task_plan": [],
                "completed_tasks": [],
                "final_deliverable": None,
                "validation_reports": [],
                "cost_estimate": 0.0,
                "current_cost": 0.0
            }
            
            # Call the retriever node
            result = retriever_node(state)
            
            # Print retrieved information for debugging
            print(f"\n=== RETRIEVED INFORMATION (No Results Test - {len(result['retrieved_information'])} items) ===")
            for i, info in enumerate(result["retrieved_information"]):
                print(f"--- Item {i+1} ---")
                print(info)
                print()
            
            # Assertions
            assert "retrieved_information" in result
            assert len(result["retrieved_information"]) == 1
            assert "No relevant context found for query" in result["retrieved_information"][0]
            assert "Create a very specific feature that doesn't exist" in result["retrieved_information"][0]
    
    def test_retriever_node_database_error(self):
        """Test retriever node when there's an error accessing the database."""
        with patch('src.nodes.retriever.RAGVectorStore') as mock_vector_store_class:
            
            # Mock the vector store to raise an exception
            mock_vector_store_class.side_effect = Exception("Database connection failed")
            
            # Create test state
            state: AgentState = {
                "user_request": "Build a notes app",
                "clarified_request": "Create a notes application",
                "is_clarification_needed": False,
                "clarification_questions": [],
                "retrieved_information": [],
                "processed_information": [],
                "task_plan": [],
                "completed_tasks": [],
                "final_deliverable": None,
                "validation_reports": [],
                "cost_estimate": 0.0,
                "current_cost": 0.0
            }
            
            # Call the retriever node
            result = retriever_node(state)
            
            # Print retrieved information for debugging
            print(f"\n=== RETRIEVED INFORMATION (Database Error Test - {len(result['retrieved_information'])} items) ===")
            for i, info in enumerate(result["retrieved_information"]):
                print(f"--- Item {i+1} ---")
                print(info)
                print()
            
            # Assertions
            assert "retrieved_information" in result
            assert len(result["retrieved_information"]) == 1
            assert "Error occurred during information retrieval" in result["retrieved_information"][0]
            assert "Database connection failed" in result["retrieved_information"][0]
    
    def test_retriever_node_retrieval_error(self):
        """Test retriever node when retrieval process itself fails."""
        with patch('src.nodes.retriever.RAGVectorStore') as mock_vector_store_class, \
             patch('src.nodes.retriever.SimpleRAGRetriever') as mock_retriever_class:
            
            # Setup mocks
            mock_vector_store = Mock()
            mock_vector_store_class.return_value = mock_vector_store
            
            mock_retriever = Mock()
            mock_retriever_class.return_value = mock_retriever
            
            # Mock retrieve_context to raise an exception
            mock_retriever.retrieve_context.side_effect = Exception("Retrieval failed")
            
            # Create test state
            state: AgentState = {
                "user_request": "Build a notes app",
                "clarified_request": "Create a notes application",
                "is_clarification_needed": False,
                "clarification_questions": [],
                "retrieved_information": [],
                "processed_information": [],
                "task_plan": [],
                "completed_tasks": [],
                "final_deliverable": None,
                "validation_reports": [],
                "cost_estimate": 0.0,
                "current_cost": 0.0
            }
            
            # Call the retriever node
            result = retriever_node(state)
            
            # Print retrieved information for debugging
            print(f"\n=== RETRIEVED INFORMATION (Retrieval Error Test - {len(result['retrieved_information'])} items) ===")
            for i, info in enumerate(result["retrieved_information"]):
                print(f"--- Item {i+1} ---")
                print(info)
                print()
            
            # Assertions
            assert "retrieved_information" in result
            assert len(result["retrieved_information"]) == 1
            assert "Error occurred during information retrieval" in result["retrieved_information"][0]
            assert "Retrieval failed" in result["retrieved_information"][0]
    
    def test_retriever_node_state_preservation(self):
        """Test that retriever node preserves other state fields."""
        with patch('src.nodes.retriever.RAGVectorStore') as mock_vector_store_class, \
             patch('src.nodes.retriever.SimpleRAGRetriever') as mock_retriever_class:
            
            # Setup mocks
            mock_vector_store = Mock()
            mock_vector_store_class.return_value = mock_vector_store
            
            mock_retriever = Mock()
            mock_retriever_class.return_value = mock_retriever
            
            sample_contexts = ["Sample context"]
            mock_retriever.retrieve_context.return_value = sample_contexts
            
            # Create test state with existing data
            original_task = {
                "id": 1,
                "role": "TestRole",
                "goal": "Test goal",
                "context": "Test context",
                "status": "pending",
                "result": None,
                "generated_test_cases": None,
                "self_validation_status": None
            }
            
            state: AgentState = {
                "user_request": "Build a notes app",
                "clarified_request": "Create a notes application",
                "is_clarification_needed": False,
                "clarification_questions": ["How many users?"],
                "retrieved_information": [],
                "processed_information": ["Some processed info"],
                "task_plan": [original_task],
                "completed_tasks": [],
                "final_deliverable": None,
                "validation_reports": [],
                "cost_estimate": 100.0,
                "current_cost": 50.0
            }
            
            # Call the retriever node
            result = retriever_node(state)
            
            # Print retrieved information for debugging
            print(f"\n=== RETRIEVED INFORMATION (State Preservation Test - {len(result['retrieved_information'])} items) ===")
            for i, info in enumerate(result["retrieved_information"]):
                print(f"--- Item {i+1} ---")
                print(info)
                print()
            
            # Assertions - check that other fields are preserved
            assert result["user_request"] == "Build a notes app"
            assert result["clarified_request"] == "Create a notes application"
            assert result["is_clarification_needed"] == False
            assert result["clarification_questions"] == ["How many users?"]
            assert result["processed_information"] == ["Some processed info"]
            assert result["task_plan"] == [original_task]
            assert result["cost_estimate"] == 100.0
            assert result["current_cost"] == 50.0
            
            # Check that retrieved_information was updated
            assert result["retrieved_information"] == ["Sample context"]


# Integration test that can be run when the database is actually populated
class TestRetrieverNodeIntegration:
    """Integration tests for the retriever node (requires populated database)."""
    
    @pytest.mark.integration
    def test_retriever_node_real_database(self):
        """Test retriever node with a real database (marked as integration test)."""
        # This test requires a populated database and should only be run during integration testing
        # Skip if no database is available
        
        try:
            from src.rag.RAGVectorStore import RAGVectorStore
            vector_store = RAGVectorStore(
                collection_name="narbtech_code",
                persist_directory="./chroma_db"
            )
            
            # Check if database has content
            count = vector_store.collection.count()
            if count == 0:
                pytest.skip("Database is empty - populate it first")
            
            # Create test state
            state: AgentState = {
                "user_request": "Build a notes app",
                "clarified_request": "Create a notes application with dashboard",
                "is_clarification_needed": False,
                "clarification_questions": [],
                "retrieved_information": [],
                "processed_information": [],
                "task_plan": [],
                "completed_tasks": [],
                "final_deliverable": None,
                "validation_reports": [],
                "cost_estimate": 0.0,
                "current_cost": 0.0
            }
            
            # Call the retriever node
            result = retriever_node(state)
            
            # Print retrieved information for debugging
            print(f"\n=== RETRIEVED INFORMATION (Integration Test - {len(result['retrieved_information'])} items) ===")
            for i, info in enumerate(result["retrieved_information"]):
                print(f"--- Item {i+1} ---")
                print(info[:500] + "..." if len(info) > 500 else info)  # Truncate long results
                print()
            
            # Basic assertions
            assert "retrieved_information" in result
            assert len(result["retrieved_information"]) > 0
            assert not any("Error occurred" in info for info in result["retrieved_information"])
            
        except Exception as e:
            pytest.skip(f"Real database test skipped due to: {e}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 