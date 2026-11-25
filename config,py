import os
import requests

# Replace with your Firebase Web API Key (or set via environment variable)
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "AIzaSyB27WVbmU-EjelkqOUdnABEhyvhM7li4ag")
OLLAMA_MODEL = "gemma3"
OLLAMA_URL = "http://localhost:11434/api/generate"
DB_FILE = "fluxora_db.json"

def firebase_login(email: str, password: str):
    """Authenticates users via Firebase REST API with a demo fallback mode."""
    if FIREBASE_API_KEY == "YOUR_FIREBASE_WEB_API_KEY":
        if email in ["captain@fluxora.com", "authority@fluxora.com"] and password == "123456":
            return True, "Demo Login Success"
        return False, "Add your Firebase Web API Key in config.py (or use captain@fluxora.com / 123456)."

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    try:
        res = requests.post(
            url,
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10
        )
        if res.status_code == 200:
            return True, "Authenticated via Firebase"
        err = res.json().get("error", {}).get("message", "Login Failed")
        return False, err
    except Exception as e:
        return False, f"Connection Error: {str(e)}"
