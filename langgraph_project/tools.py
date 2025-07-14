import os
from tavily import TavilyClient
from langchain_core.tools import Tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- Configuration ---
VECTORSTORE_DIR = "vectorstore"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# --- Tavily Web Search Tool ---
# Initialize the Tavily client directly
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def tavily_search_func(query: str):
    """Performs a search using the Tavily client and returns the results."""
    try:
        # The .search method returns a dictionary; we're interested in the 'results' key.
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        return response['results']
    except Exception as e:
        return f"An error occurred during search: {e}"

# Create a LangChain Tool from the custom search function
search_tool = Tool(
    name="tavily_search",
    func=tavily_search_func,
    description="A search engine optimized for comprehensive, accurate, and trusted results. Useful for general web searches, current events, and broad topics.",
)

# --- RAG Knowledge Base Tool ---
def create_rag_tool():
    """Creates a RAG tool for searching the local knowledge base."""
    try:
        # Load the vector store and create a retriever
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vectorstore = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embeddings)
        retriever = vectorstore.as_retriever()

        # The function that the tool will execute
        def rag_search_func(query: str):
            """Performs a search on the local knowledge base."""
            return retriever.invoke(query)

        # Create the LangChain Tool
        return Tool(
            name="knowledge_base_search",
            func=rag_search_func,
            description="Searches the local knowledge base for specific information about AI advancements, ethics, and internal documents. Use this for detailed, internal knowledge.",
        )
    except Exception as e:
        print(f"Failed to create RAG tool: {e}")
        # Return a dummy tool that reports the error
        return Tool(
            name="knowledge_base_search",
            func=lambda query: f"Error: RAG tool not available. Could not load vector store. Details: {e}",
            description="Knowledge base is currently unavailable.",
        )

# --- Initialize Tools ---
rag_tool = create_rag_tool()
