# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings loaded from environment variables."""

    POSTGRES_CONNECTION = os.getenv("POSTGRES_CONNECTION")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
