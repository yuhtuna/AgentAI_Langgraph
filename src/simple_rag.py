from typing import List, Dict
from src.create_vectorstore import RAGVectorStore, ProjectProcessor

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

# Test with simplified retriever
def test_simplified_retriever():
    projects = [("knowledge_base/narbhacks-main", "notes app")]
    
    # Setup
    processor = ProjectProcessor()
    vector_store = RAGVectorStore()
    vector_store.clear_collection()
    
    # Process
    all_chunks = []
    for project_path, project_name in projects:
        chunks = processor.process_project(project_path, project_name)
        all_chunks.extend(chunks)
    
    vector_store.add_chunks(all_chunks)
    
    # Test simplified retriever
    simple_retriever = SimpleRAGRetriever(vector_store)
    contexts = simple_retriever.retrieve_context("Create a notes app homepage")
    
    print(f"\n=== SIMPLIFIED RETRIEVER RESULTS ===")
    print(f"Retrieved {len(contexts)} contexts")
    
    if contexts:
        print("\nFirst context:")
        print(contexts[0][:500] + "..." if len(contexts[0]) > 500 else contexts[0])
    
    return contexts

# Uncomment to test:
test_simplified_retriever()