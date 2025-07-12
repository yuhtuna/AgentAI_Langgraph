from typing import Any

class ExampleEdge:
    """
    Example implementation of an edge in the LangGraph.
    """
    def __init__(self, source_id: str, target_id: str, weight: float = 1.0, metadata: Any = None):
        self.source_id = source_id
        self.target_id = target_id
        self.weight = weight
        self.metadata = metadata
