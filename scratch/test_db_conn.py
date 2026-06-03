import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
print("Trying to connect to URL from .env:", database_url)

if "sslmode" not in database_url:
    separator = "&" if "?" in database_url else "?"
    database_url = f"{database_url}{separator}sslmode=require"

try:
    conn = psycopg2.connect(database_url)
    print("SUCCESS: Connected to database!")
    
    with conn.cursor() as cur:
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
        print("SUCCESS: Table checked/created successfully!")
        
    conn.commit()
    conn.close()
except Exception as e:
    print("FAILED to connect:", e)
