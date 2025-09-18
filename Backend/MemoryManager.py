import chromadb
from sentence_transformers import SentenceTransformer
import json
import os
import time

print("MemoryManager: Initializing...")
client = chromadb.PersistentClient(path="memory_db")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
collection = client.get_or_create_collection(name="jarvis_memory")
print("MemoryManager: Ready.")

request_file = r"Frontend\Files\memory_request.data"
response_file = r"Frontend\Files\memory_response.data"

def store_memory(text_to_remember):
    embedding = embedding_model.encode(text_to_remember).tolist()
    doc_id = f"mem_{collection.count() + 1}"    # For simple counter or a timestamp for unique IDs
    collection.add(
        embeddings=[embedding],
        documents=[text_to_remember],
        ids=[doc_id]
    )
    print(f"MemoryManager: Stored '{text_to_remember}'")
    
    
def retrieve_memories(query, num_results=3):
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=num_results
    )
    return results['documents'][0] if results.get('documents') else []

if __name__ == "__main__":
    while True:
        try:
            if os.path.exists(request_file) and os.path.getsize(request_file) > 0:
                with open(request_file, 'r') as f:
                    data = json.load(f)
                    
                action = data.get("action")
                payload = data.get("payload")
                
                if action == "retrieve":
                    memories = retrieve_memories(payload)
                    with open(response_file, 'w') as f:
                        json.dump(memories, f)
                    print(f"MemoryManager: Retrieved memories for query '{payload}'")
                    
                elif action == "store":
                    store_memory(payload)
                    with open(response_file, 'w') as f:
                        f.write("")
                        
                with open(request_file, 'w') as f:
                    f.write("")
                    
        except Exception as e:
            print(f"Error in MemoryManager: {e}")
            
            if os.path.exists(request_file):
                with open(request_file, 'w') as f: f.write("")
            if os.path.exists(response_file):
                with open(response_file, 'w') as f: f.write("")
        
        time.sleep(0.5)