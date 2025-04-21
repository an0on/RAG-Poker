# RAG-Service mit FastAPI, Supabase und OLAMA (Hardcoded Test)

## Starten (lokal)

```bash
docker build -t rag-service .
docker run -p 8000:8000 rag-service
```

## Endpoint

POST /ask

Body:
{
  "question": "Was ist § 1 BGB?"
}
