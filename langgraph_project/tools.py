from langchain_community.tools.tavily_search import TavilySearchResults

# Initialize the search tool
# max_results=5 specifies the number of search results to return
search_tool = TavilySearchResults(max_results=5)
