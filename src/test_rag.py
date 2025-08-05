from src.create_vectorstore import RAGVectorStore, RAGRetriever, ProjectProcessor
from typing import List, Dict, Optional, Tuple 


def setup_rag_system(narbtech_projects: List[Tuple[str, str]], clear_existing: bool = False) -> RAGRetriever: 
    print("Setting up RAG system...")
    processor = ProjectProcessor()
    vector_store = RAGVectorStore()
    
    if clear_existing:
        print("Clearing existing collection...")
        vector_store.clear_collection()
    
    all_chunks = [] 
    for project_path, project_name in narbtech_projects: 
        print(f"Processing project: {project_name} at {project_path}") 
        chunks = processor.process_project(project_path, project_name)
        all_chunks.extend(chunks)
    
    print(f"Adding {len(all_chunks)} chunks to vector store")
    vector_store.add_chunks(all_chunks)
    
    retriever = RAGRetriever(vector_store)
    print("RAG system setup complete")
    return retriever, vector_store, all_chunks

def debug_vector_store(vector_store: RAGVectorStore, chunks: List):
    """Debug function to check what's in the vector store"""
    print("\n=== DEBUGGING VECTOR STORE ===")
    
    # Check collection stats
    try:
        collection_count = vector_store.collection.count()
        print(f"Total documents in collection: {collection_count}")
    except Exception as e:
        print(f"Error getting collection count: {e}")
    
    # Print sample chunk info
    print(f"\nSample chunks processed:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"Chunk {i+1}:")
        print(f"  - File: {chunk.file_path}")
        print(f"  - Framework: {chunk.framework}")
        print(f"  - Type: {chunk.file_type}")
        print(f"  - Description: {chunk.description}")
        print(f"  - Content preview: {chunk.content[:100]}...")
        print()
    
    # Test basic search
    print("Testing basic searches:")
    test_queries = [
        "notes app homepage",
        "React component",
        "function",
        "page",
        "dashboard"
    ]
    
    for query in test_queries:
        try:
            # Try direct vector store search
            results = vector_store.search(query, n_results=3)
            print(f"Query '{query}': Found {len(results)} results")
            
            if results:
                for i, result in enumerate(results[:1]):  # Show first result
                    metadata = result['metadata']
                    print(f"  Result {i+1}: {metadata['file_path']} ({metadata['framework']})")
            else:
                print(f"  No results for '{query}'")
        except Exception as e:
            print(f"  Error searching for '{query}': {e}")
        print()

projects = [
    ("knowledge_base/narbhacks-main", "notes app"),
]

# Set up the system with debugging
retriever, vector_store, chunks = setup_rag_system(projects, clear_existing=True)

# Debug what's in the store
debug_vector_store(vector_store, chunks)

# Test retrieval with more debugging
print("\n=== TESTING RETRIEVAL ===")
test_query = "Create a notes app homepage"
print(f"Testing query: '{test_query}'")

# Test the individual search methods in RAGRetriever
print(f"UI check: {retriever._mentions_ui(test_query)}")
print(f"Backend check: {retriever._mentions_backend(test_query)}")
print(f"Auth check: {retriever._mentions_auth(test_query)}")

# Try direct search on vector store
print("\nDirect vector store search:")
direct_results = vector_store.search(test_query, n_results=5)
print(f"Direct search found {len(direct_results)} results")

for i, result in enumerate(direct_results[:2]):
    metadata = result['metadata']
    print(f"Result {i+1}: {metadata['file_path']} ({metadata['framework']}) - Distance: {result.get('distance', 'N/A')}")

# Test retriever
print("\nUsing RAGRetriever:")
contexts = retriever.retrieve_context(test_query)
print(f"Retrieved {len(contexts)} contexts")

if contexts:
    print("\nFirst context preview:")
    print(contexts[0][:500] + "..." if len(contexts[0]) > 500 else contexts[0])
else:
    print("No contexts retrieved - investigating...")
    
    # Try a simpler query
    simple_contexts = retriever.retrieve_context("page")
    print(f"Simple query 'page' returned {len(simple_contexts)} contexts")
    
    if simple_contexts:
        print("Simple query worked - issue might be with complex query processing")
    else:
        print("Even simple queries aren't working - checking collection directly...")
        
        # Get all documents to see what's there
        try:
            all_docs = vector_store.collection.get()
            print(f"Collection contains {len(all_docs['ids'])} documents")
            if all_docs['ids']:
                print(f"Sample IDs: {all_docs['ids'][:3]}")
        except Exception as e:
            print(f"Error getting all docs: {e}")

