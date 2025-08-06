from typing import List, Dict
from src.rag.RAGVectorStore import RAGVectorStore
from src.rag.ProjectProcessor import ProjectProcessor

class SimpleRAGRetriever: 
    def __init__(self, vector_store: RAGVectorStore): 
        self.vector_store = vector_store

    def retrieve_context(self, user_request: str, max_chunks: int = 5) -> List[str]: 
        """Simplified retrieval - just search and return top results"""
        print(f"Searching for: '{user_request}'")
        
        # Direct search without complex filtering
        results = self.vector_store.search(
            query=user_request,
            n_results=max_chunks
        )
        
        print(f"Found {len(results)} results")
        
        # Format results
        contexts = []
        for i, result in enumerate(results):
            context = self._format_context(result)
            contexts.append(context)
            print(f"Result {i+1}: {result['metadata']['file_path']} (distance: {result.get('distance', 'N/A')})")
        
        return contexts
    
    def _format_context(self, result: Dict) -> str:
        """Format search result into context string"""
        metadata = result['metadata']
        
        context_parts = [
            f"// File: {metadata['file_path']}",
            f"// Project: {metadata['project_name']}",
            f"// Type: {metadata['file_type']} ({metadata['framework']})",
            f"// Description: {metadata['description']}",
        ]
        
        if metadata.get('dependencies'):
            context_parts.append(f"// Dependencies: {', '.join(metadata['dependencies'])}")
        
        context_parts.append("")  # Empty line
        
        # Extract actual code content
        content = result['content']
        if "Code:\n" in content:
            code_content = content.split("Code:\n", 1)[1]
            context_parts.append(code_content)
        else:
            context_parts.append(content)
        
        return "\n".join(context_parts)