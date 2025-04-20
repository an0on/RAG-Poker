# RAG-Service mit FastAPI, Supabase und OLAMA

## Starten (lokal)

```bash
docker build -t rag-service .
docker run -p 8000:8000 \
  -e SUPABASE_URL=deine-url \
  -e SUPABASE_KEY=dein-key \
  -e OLLAMA_URL=http://localhost:11434 \
  rag-service
```

## Endpoint

`POST /ask`

**Body:**
```json
{
  "question": "Was ist § 1 BGB?"
}
```

## Antwort:
```json
{
  "answer": "Antwort von OLAMA mit Kontext aus Supabase"
}
```
