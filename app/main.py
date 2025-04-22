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
