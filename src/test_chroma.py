
import chromadb

# Method 1: Quick count check
def quick_count_check():
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        collection = client.get_collection("narbtech_code")
        count = collection.count()
        print(f"Documents in collection: {count}")
        return count
    except Exception as e:
        print(f"Error: {e}")
        return 0

# Method 2: List all collections
def list_collections():
    client = chromadb.PersistentClient(path="./chroma_db")
    collections = client.list_collections()
    print(f"Collections: {[c.name for c in collections]}")
    for c in collections:
        try:
            print(f"  - {c.name}: {c.count()} documents")
        except:
            print(f"  - {c.name}: Error getting count")

# Method 3: Test a simple search
def test_simple_search():
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        collection = client.get_collection("narbtech_code")
        results = collection.query(query_texts=["React"], n_results=1)
        print(f"Search test results: {len(results['documents'][0])} found")
        if results['documents'][0]:
            metadata = results['metadatas'][0][0]
            print(f"  Sample result: {metadata.get('file_path', 'No file path')}")
    except Exception as e:
        print(f"Search error: {e}")

# Run all quick checks
if __name__ == "__main__":
    print("=== QUICK CHROMADB CHECKS ===")
    quick_count_check()
    list_collections() 
    test_simple_search()