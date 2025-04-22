from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, HttpUrl
from supabase import create_client, Client
import os
import requests
import logging
import asyncio  # Für asynchrone Operationen

# Logging einrichten
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
CONTEXT_CHUNKS = int(os.getenv("CONTEXT_CHUNKS", 5))  # Anzahl der Kontext-Chunks konfigurierbar

# Validierung der Umgebungsvariablen
if not SUPABASE_URL:
    raise ValueError("Umgebungsvariable SUPABASE_URL fehlt.")
if not SUPABASE_KEY:
    raise ValueError("Umgebungsvariable SUPABASE_KEY fehlt.")
try:
    HttpUrl(SUPABASE_URL)
except ValueError:
    raise ValueError(f"Ungültiges Format für SUPABASE_URL: {SUPABASE_URL}")

# Erstellen des Supabase-Clients
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logging.error(f"Fehler beim Erstellen des Supabase-Clients: {e}")
    raise Exception(f"Fehler beim Erstellen des Supabase-Clients: {e}")

app = FastAPI()

class Question(BaseModel):
    question: str

@app.get("/")
async def read_root():
    return {"message": "Bin bereit. Frag mich was unter POST /ask."}

@app.post("/ask")
async def ask_question(payload: Question):
    question = payload.question
    logging.info(f"Eingegangene Frage: {question}")

    try:
        # tsquery aufbereiten (PostgreSQL-kompatibel, mit deutscher Sprachkonfiguration)
        cleaned_query = " & ".join(
            filter(None, (word.strip().lower().replace("?", "").replace(",", "") for word in question.split()))
        )
        logging.info(f"Aufbereitete tsquery: {cleaned_query}")

        # SQL-Abfrage direkt gegen Supabase (PostgREST RPC oder SQL-Raw Query via REST API)
        sql_query = f"""
            SELECT content FROM regelwerk_chunks
            WHERE to_tsvector('german', content) @@ to_tsquery('german', '{cleaned_query}')
            LIMIT {CONTEXT_CHUNKS};
        """
        response = supabase.rpc('sql', {'q': sql_query}).execute()
        data = response.data or []

        logging.info(f"Anzahl der gefundenen Chunks: {len(data)}")

    except Exception as e:
        logging.error(f"Supabase Fehler bei SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Supabase Fehler: {str(e)}")

    chunks = [r["content"] for r in data]

    if not chunks:
        logging.warning("Keine passenden Inhalte in der Datenbank gefunden.")
        raise HTTPException(status_code=404, detail="Keine passenden Inhalte gefunden.")

    context = "\n".join(chunks)
    prompt = f"""Beantworte die Frage basierend auf folgendem Kontext.
Du bist Pokercoach, Pokerdealer und vor allem Floorman. Antworte klar und präzise.

Kontext:
{context}

Frage: {question}

Antwort:"""

    try:
        response_ollama = await asyncio.to_thread(
            requests.post,
            f"{OLLAMA_HOST}/api/generate",
            json={"model": "llama3", "prompt": prompt},
            timeout=60
        )
        response_ollama.raise_for_status()
        content = response_ollama.json().get("response", "Keine Antwort erhalten.")
        logging.info(f"Ollama Antwort erhalten: {content[:100]}...")
        return {"antwort": content.strip()}

    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama Fehler: {e}")
        raise HTTPException(status_code=502, detail=f"Ollama Fehler: {str(e)}")
