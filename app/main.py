from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os
import requests

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Fehlende Umgebungsvariablen: SUPABASE_URL und/oder SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class QuestionRequest(BaseModel):
    question: str

def embed_text(text: str):
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]

def query_supabase(embedding):
    response = supabase.rpc("match_documents", {
        "query_embedding": embedding,
        "match_count": 5
    }).execute()
    return [match["content"] for match in response.data]

def query_ollama(prompt: str):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    return response.json()["response"]

@app.post("/ask")
def ask_question(data: QuestionRequest):
    embedding = embed_text(data.question)
    context_chunks = query_supabase(embedding)
    context = "\n---\n".join(context_chunks)
    full_prompt = f"Kontext:\n{context}\n\nFrage: {data.question}\nAntwort:"
    answer = query_ollama(full_prompt)
    return {"answer": answer}
