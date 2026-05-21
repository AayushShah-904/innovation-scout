import psycopg2
import os

def get_connection():
    """Returns a psycopg2 connection using DATABASE_URL env var (Supabase/Render)
    or falls back to individual env vars for local development."""
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

def init_database():
    conn = get_connection()

    with conn.cursor() as cur:
        # Enable the pgvector extension so PostgreSQL can store and query 384-dimensional AI embeddings
        cur.execute("create extension if not exists vector")

        cur.execute(""" 
        create table if not exists documents(
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        source TEXT NOT NULL,
        embedding vector(384)
        )
        """)

        print("Database initilized successfully")
    
    conn.commit()
    conn.close()

if __name__=="__main__":
    init_database()