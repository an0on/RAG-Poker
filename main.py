from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
import requests
from dotenv import load_dotenv

# Load env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama-server:11434")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Fehlende Umgebungsvariablen: SUPABASE_URL und/oder SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI()

class Question(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Bin bereit. Frag mich was unter POST /ask."}

@app.post("/ask")
def ask_question(payload: Question):
    question = payload.question

    try:
        result = (
    supabase
    .table("regelwerk_chunks")
    .select("text")
    .text_search("text", question)
    .execute()
)

chunks = [r["text"] for r in result.data[:5]] if result.data else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase Error: {str(e)}")

    chunks = [r["text"] for r in result.data] if result.data else []

    if not chunks:
        raise HTTPException(status_code=404, detail="Keine passenden Inhalte gefunden.")

    context = "\n".join(chunks)
    prompt = f"""Beantworte die Frage basierend auf folgendem Kontext.
Du bist Pokercoach, Pokerdealer und vor allem Floorman. Antworte klar und präzise.

Kontext:
{context}

Frage: {question}

Antwort:"""

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": "llama3", "prompt": prompt},
            timeout=60
        )
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama Error: {str(e)}")

    content = response.json().get("response", "Keine Antwort erhalten.")
    return {"antwort": content.strip()}
