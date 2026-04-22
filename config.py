import os
from dotenv import load_dotenv

load_dotenv()

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "")
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "")
FB_USER_PSID = os.getenv("FB_USER_PSID", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "")

REQUIRED = [
    ("FB_PAGE_ACCESS_TOKEN", FB_PAGE_ACCESS_TOKEN),
    ("FB_VERIFY_TOKEN", FB_VERIFY_TOKEN),
    ("OPENROUTER_API_KEY", OPENROUTER_API_KEY),
    ("GOOGLE_SHEET_ID", GOOGLE_SHEET_ID),
    ("GOOGLE_CREDENTIALS_JSON", GOOGLE_CREDENTIALS_JSON),
]

def validate():
    missing = [name for name, val in REQUIRED if not val]
    if missing:
        raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")
