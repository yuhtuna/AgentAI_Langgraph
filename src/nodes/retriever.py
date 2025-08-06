from src.state import AgentState
from src.rag.RAGVectorStore import RAGVectorStore
from src.rag.RAGRetriever import SimpleRAGRetriever
from typing import List
import os

def retriever_node(state: AgentState) -> AgentState:
    """
    A node that retrieves information from the vector database.
    
    This node queries the vector database using the clarified_request to fetch 
    relevant context, code snippets, and past solutions from the knowledge base.
    
    Args:
        state (AgentState): The current state of the agent.
        
    Returns:
        AgentState: The updated state with retrieved_information populated.
    """
    print("🔍 Starting retrieval process...")
    
    # Get the clarified request for searching
    query = state.get("clarified_request", "").strip()
    
    if not query:
        print("⚠️ No clarified request found, using user_request as fallback")
        query = state.get("user_request", "").strip()
    
    if not query:
        print("❌ No query available for retrieval")
        state["retrieved_information"] = ["No query available for information retrieval"]
        return state
    
    print(f"🔍 Searching for: '{query}'")
    
    try:
        # Initialize the vector store
        # Use a standard collection name and persist directory
        vector_store = RAGVectorStore(
            collection_name="narbtech_code", 
            persist_directory="./chroma_db"
        )
        
        # Initialize the retriever
        retriever = SimpleRAGRetriever(vector_store)
        
        # Perform the search
        # Retrieve more chunks for comprehensive context
        retrieved_contexts = retriever.retrieve_context(
            user_request=query,
            max_chunks=8  # Get more relevant chunks for better context
        )
        
        if retrieved_contexts:
            print(f"✅ Retrieved {len(retrieved_contexts)} relevant contexts")
            
            # Update the state with retrieved information
            state["retrieved_information"] = retrieved_contexts
            
            # Log the first result for debugging
            if retrieved_contexts:
                first_result = retrieved_contexts[0][:200] + "..." if len(retrieved_contexts[0]) > 200 else retrieved_contexts[0]
                print(f"📄 First result preview: {first_result}")
        else:
            print("⚠️ No relevant context found in the knowledge base")
            state["retrieved_information"] = [
                f"No relevant context found for query: '{query}'. "
                "The knowledge base may be empty or the query may not match existing content."
            ]
    
    except Exception as e:
        print(f"❌ Error during retrieval: {str(e)}")
        # Provide fallback information in case of error
        state["retrieved_information"] = [
            f"Error occurred during information retrieval: {str(e)}. "
            "Proceeding without retrieved context."
        ]
    
    print(f"🏁 Retrieval complete. Found {len(state['retrieved_information'])} information items")
    return state