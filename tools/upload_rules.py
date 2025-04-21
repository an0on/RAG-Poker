import os
from sentence_transformers import SentenceTransformer
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RULES_FILE = os.getenv("RULES_FILE", "rules.txt")

model = SentenceTransformer('all-MiniLM-L6-v2')
client = create_client(SUPABASE_URL, SUPABASE_KEY)

def chunk_text(text, chunk_size=500, overlap=100):
    start = 0
    chunks = []
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

with open(RULES_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

chunks = chunk_text(content)

for idx, chunk in enumerate(chunks):
    embedding = model.encode(chunk).tolist()
    client.table("regelwerk_chunks").insert({
        "content": chunk,
        "embedding": embedding
    }).execute()
    print(f"Hochgeladen: Chunk {idx + 1}/{len(chunks)}")
