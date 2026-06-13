import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

# Read Gemini API key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

# Create Gemini client
client = genai.Client(api_key=API_KEY)

print("[rag.py] Gemini client ready.")