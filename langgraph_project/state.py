from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    The central state object that will be passed between nodes.
    It holds all the information our agents will work with.
    """
    task: str
    plan: str
    draft: str
    review: str
    search_results: List[str]  # Add a list to store search results
    # `messages` is a special field that will contain the conversation history.
    # `add_messages` is a helper function that appends messages to this list.
    messages: Annotated[list[AnyMessage], add_messages]
