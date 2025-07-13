import os
from tavily import TavilyClient
from langchain_core.tools import Tool

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
    description="A search engine optimized for comprehensive, accurate, and trusted results. Useful for researching topics and answering questions.",
)
