from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# Testabfrage – passe das Wort ggf. an
query = "Sidepot"
response = supabase.table("regelwerk_chunks").select("content").text_search("content", query).execute()

print("Treffer:", len(response.data))
for r in response.data[:5]:
    print("-", r["content"][:100])  # Erste 100 Zeichen anzeigen
