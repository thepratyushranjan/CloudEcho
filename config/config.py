import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings loaded from environment variables."""

    POSTGRES_CONNECTION = os.getenv("POSTGRES_CONNECTION")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
