import os
from google import genai
from tavily import TavilyClient

# Ensure environment variables are loaded if using a package like python-dotenv
# For simplicity, we assume they are either in the env or loaded before this module is accessed.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GEMINI_API_KEY or not TAVILY_API_KEY:
    print("WARNING: GEMINI_API_KEY or TAVILY_API_KEY not found in environment.")

# Initialize shared clients
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
