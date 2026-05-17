import psycopg2
from sentence_transformers import SentenceTransformer

print("Loading sentence-transformers model (all-MiniLM-L6-v2)...")

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

print("Model loaded successfully.")

def get_db_connection():
    """Establishes a connection to the pgvector PostgreSQL container."""
    return psycopg2.connect(
        dbname="innovation_db",
        user="admin",
        password="12345",
        host="localhost",
        port="5432"
    )

def save_document(doc:dict)->bool:
    """Saves a document to the vector database after generating an embedding."""

    text_to_embed = f"{doc['title']} {doc['summary']}"
    

    try:
        encoder=get_model()
        embedding = encoder.encode(text_to_embed).tolist()

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO documents (title, summary, url, source, embedding)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
        """,(
            doc["title"],
            doc["summary"],
            doc["url"],
            doc["source"],
            embedding
        ))
        
        conn.commit()
        cur.close()
        print(f"Saved document: {doc['title']}")
    except Exception as e:
        print(f"Error saving to database: {e}")
        conn.rollback()
    finally:
        conn.close()

def search_similar_documents(query:str,limit:int=5)->list[dict]:
    """Searches for documents similar to the query using cosine similarity"""
    
    if not query:
        return []
    
    results=[]
    
    try:
        encoder=get_model()
        query_vector = encoder.encode(query).tolist()
        
        conn=get_db_connection()
        cur=conn.cursor()

        cur.execute("""
                    SELECT id, title, summary, url, source, (embedding <=> %s::vector) as distance
                    FROM documents
                    ORDER BY distance ASC
                    LIMIT %s;
                """, (query_vector, limit))

        rows = cur.fetchall()
        for row in rows:
            results.append({
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "url": row[3],
            "source": row[4],
            "distance": float(row[5])
        })
    
    except Exception as e:
        print(f"Error searching database: {e}")
    
    finally:
        cur.close()
        conn.close()

    return results

if __name__ == "__main__":

    print("\n--- Running Vector Store Test ---")

    mock_doc = {
        "title": "Agentic Workflows in Enterprise Search Systems",
        "summary": "An exploration of LangGraph architectures paired with pgvector to solve R&D tech scouting challenges.",
        "url": "https://arxiv.org/abs/test.agentic",
        "source": "arxiv"
    }
    
    print("Testing document ingestion...")
    save_document(mock_doc)
    print("Ingestion complete.")
    
    search_prompt = "AI orchestration frameworks for matching technology targets"
    print(f"\nTesting vector similarity search for: '{search_prompt}'")
    matched_papers = search_similar_documents(search_prompt, limit=1)
    
    print("\n--- MATCH FOUND ---")
    for paper in matched_papers:
        print(f"Title: {paper['title']}")
        print(f"Source: {paper['source']}")
        print(f"Cosine Distance: {paper['distance']:.4f} (Lower is closer)")