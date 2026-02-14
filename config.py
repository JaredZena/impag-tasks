from dotenv import load_dotenv
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
allowed_emails = [
    e.strip().lower()
    for e in os.getenv("ALLOWED_EMAILS", "").split(",")
    if e.strip()
]
