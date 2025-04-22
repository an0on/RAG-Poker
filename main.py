@app.post("/ask")
def ask_question(payload: Question):
    question = payload.question

    # 🧼 tsquery vorbereiten: Satzzeichen raus, Wörter mit & verknüpfen
    ts_query = ' & '.join(
        question.replace("?", "").replace("!", "").replace(",", "").replace(".", "").split()
    )

    try:
        result = (
            supabase
            .table("regelwerk_chunks")
            .select("content")
            .text_search("content", ts_query)
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase Error: {str(e)}")

    chunks = [r["content"] for r in result.data[:5]] if result.data else []

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
