import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Fehlende Umgebungsvariablen!")
    exit()

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase-Client erfolgreich erstellt.")

    # Einfache Abfrage zum Testen der Verbindung
    response = supabase.table("regelwerk_chunks").select("count(*)").execute()
    if response.error is None:
        count = response.data[0]['count']
        print(f"Verbindung erfolgreich. Anzahl der Einträge in 'regelwerk_chunks': {count}")
    else:
        print(f"Fehler bei der Abfrage: {response.error}")

except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
