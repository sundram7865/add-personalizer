import anthropic
from functools import lru_cache
from app.core.config import get_settings

# Using a smaller, cheaper model. Haiku is free-tier friendly.
CLAUDE_MODEL = "claude-haiku-4-5-20251001"


@lru_cache
def get_claude_client() -> anthropic.Anthropic:
    settings = get_settings()
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)