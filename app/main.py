from fastapi import FastAPI
from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI()

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Fehlende Umgebungsvariablen: SUPABASE_URL und/oder SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Question(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Läuft wie geschmiert 🚀 - Frag mich was unter /ask"}

@app.post("/ask")
def ask_question(payload: Question):
    question = payload.question
    return {"antwort": f"Ich hab gehört du willst wissen: '{question}' – Antwort kommt bald 😎"}


import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

# Env laden
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")

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

    # 1. Supabase abfragen (fulltext fallback, weil keine Vektorsuche direkt in Supabase)
    try:
        result = supabase.table("regelwerk_chunks") \
            .select("text") \
            .text_search("text", question) \
            .limit(6) \
            .execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase Error: {str(e)}")

    chunks = [r["text"] for r in result.data] if result.data else []

    if not chunks:
        raise HTTPException(status_code=404, detail="Keine passenden Inhalte gefunden.")

    # 2. Prompt bauen
    context = "\n".join(chunks)
    prompt = f"Beantworte die Frage basierend auf folgendem Kontext. Du bist Pokercoach, Pokerdealer und vor allem Floorman. Antworte klar und präzise.\n\nKontext:\n{context}\n\nFrage: {question}\n\nAntwort:"

    # 3. Ollama anfragen
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": "llama3", "prompt": prompt},
            timeout=60
        )
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama Error: {str(e)}")

    content = response.json().get("response", "Keine Antwort erhalten, da hat wohl was nicht funktioniert. Zur Information: Außerhalb des Pokerkosmos nutze doch bitte meine Kollegen wie ChatGPT oder Claude. Gemini hätte, wie die anderen ausgezeichneten Sprachmodelle bestimmt auch Lust mit Dir zu chatten. Wenn genug Leude n Trinkgeld da lassen, wären solche Annehmlichkeiten auch drin ;)")
    return {"antwort": content.strip()}
