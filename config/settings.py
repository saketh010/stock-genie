import os
from groq import Groq
from tavily import TavilyClient

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY or not TAVILY_API_KEY:
    print("WARNING: GROQ_API_KEY or TAVILY_API_KEY not found in environment.")

# Initialize shared clients
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

# Model configuration — Llama 3.1 8B Instant is extremely fast, rate-limit friendly, and handles JSON mode perfectly
GROQ_MODEL = "llama-3.1-8b-instant"
