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

    # Korrekte Abfrage, um die Anzahl der Einträge zu erhalten
    response = supabase.table("regelwerk_chunks").select("*", count="exact").execute()
    if response.data is not None:
        count = response.count
        print(f"Verbindung erfolgreich. Anzahl der Einträge in 'regelwerk_chunks': {count}")
    else:
        print(f"Fehler bei der Abfrage: {response.error}')
    elif response.error:
        print(f"Fehler bei der Abfrage: {response.error}")

except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
