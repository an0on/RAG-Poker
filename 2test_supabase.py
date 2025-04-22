from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# Auf Deutsch konfiguriert
response = supabase.table("regelwerk_chunks") \
    .select("content") \
    .text_search("content", "Sidepot", config="german") \
    .execute()

print("Treffer:", len(response.data))
for r in response.data[:5]:
    print("-", r["content"][:100])
