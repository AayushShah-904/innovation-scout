import psycopg2

def init_database():
    conn=psycopg2.connect(
        dbname="innovation_db",
        user="admin",
        password="12345",
        host="localhost",
        port="5432"
    )

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