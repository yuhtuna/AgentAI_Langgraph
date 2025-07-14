import os
from tavily import TavilyClient
from langchain_core.tools import Tool, tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel, Field

# --- Configuration ---
VECTORSTORE_DIR = "vectorstore"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# --- Tavily Web Search Tool ---
# Initialize the Tavily client directly
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class TavilySearchInput(BaseModel):
    query: str = Field(description="The search query to find information on the web")

@tool("tavily_search", args_schema=TavilySearchInput)
def tavily_search_func(query: str) -> str:
    """Performs a search using Tavily web search for current information and latest developments."""
    try:
        # The .search method returns a dictionary; we're interested in the 'results' key.
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        return str(response['results'])
    except Exception as e:
        return f"An error occurred during search: {e}"

# The tool is now the decorated function itself
search_tool = tavily_search_func

# --- RAG Knowledge Base Tool ---
class KnowledgeBaseSearchInput(BaseModel):
    query: str = Field(description="The search query to find information in the local knowledge base")

def create_rag_tool():
    """Creates a RAG tool for searching the local knowledge base."""
    try:
        # Load the vector store and create a retriever
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vectorstore = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embeddings)
        retriever = vectorstore.as_retriever()

        @tool("knowledge_base_search", args_schema=KnowledgeBaseSearchInput)
        def rag_search_func(query: str) -> str:
            """Searches the local knowledge base for specific information about AI advancements, ethics, and internal documents."""
            docs = retriever.invoke(query)
            if docs:
                # Combine the content of all retrieved documents
                combined_content = "\n\n".join([doc.page_content for doc in docs])
                return combined_content
            else:
                return "No relevant information found in the knowledge base."

        return rag_search_func
    except Exception as e:
        print(f"Failed to create RAG tool: {e}")
        
        @tool("knowledge_base_search", args_schema=KnowledgeBaseSearchInput)
        def error_rag_search(query: str) -> str:
            """Knowledge base is currently unavailable."""
            return f"Error: RAG tool not available. Could not load vector store. Details: {e}"
        
        return error_rag_search

# --- Initialize Tools ---
rag_tool = create_rag_tool()
