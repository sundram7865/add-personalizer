import google.generativeai as genai
from functools import lru_cache
from app.core.config import get_settings

GEMINI_MODEL = "gemini-2.5-flash"

@lru_cache
def get_gemini_model():
    settings = get_settings()
    
    genai.configure(api_key=settings.gemini_api_key)
    
    return genai.GenerativeModel(GEMINI_MODEL)