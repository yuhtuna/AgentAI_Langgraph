from src.rag.RAGVectorStore import RAGVectorStore
from src.rag.ProjectProcessor import ProjectProcessor
from src.rag.RAGRetriever import SimpleRAGRetriever

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