import psycopg2
import os
from fastembed import TextEmbedding

# Cache the embedding model in memory so we don't reload it on every search
# fastembed uses ONNX Runtime (not PyTorch) — much lighter on RAM (~80MB vs ~400MB)
_model = None

def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        print("Loading fastembed model (BAAI/bge-small-en-v1.5)...")
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        print("Embedding model loaded successfully.")
    return _model

def _embed(text: str) -> list:
    """Returns a 384-dimensional embedding vector for the given text."""
    model = get_model()
    # fastembed.embed() returns a generator of numpy arrays
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()

def get_db_connection():
    """Establishes a connection using DATABASE_URL (Supabase) or individual env vars (local)."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "innovation_db"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "12345"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

def save_document(doc: dict) -> bool:
    """Saves a document to the vector database after generating an embedding."""

    # Combine title and summary so the embedding captures the full context of the paper
    text_to_embed = f"{doc['title']} {doc['summary']}"

    try:
        embedding = _embed(text_to_embed)

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

def search_similar_documents(query: str, limit: int = 5) -> list[dict]:
    """Searches for documents similar to the query using cosine similarity."""

    if not query:
        return []

    results = []

    try:
        query_vector = _embed(query)

        conn = get_db_connection()
        cur = conn.cursor()

        # Use pgvector's cosine distance operator (<=>) to find the most relevant documents
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