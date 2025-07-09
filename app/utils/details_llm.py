# -*- coding: utf-8 -*-
import os
import time
from typing import Dict
from google import genai
from google.genai import types
from config.config import Config


class PromptLoader:
    _cache = {}

    @staticmethod
    def load(file_path: str) -> str:
        abs_path = os.path.abspath(file_path)
        if abs_path in PromptLoader._cache:
            return PromptLoader._cache[abs_path]
        
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Prompt file '{abs_path}' not found.")

        with open(abs_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            PromptLoader._cache[abs_path] = content
            return content

class DetailsLlmGenerator:
    def __init__(self, llm_model_name: str = "gemini-2.5-flash", cache_hours: float = 1):
        self.llm_model_name = llm_model_name
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)

        # Load instructions
        self.system_instruction = PromptLoader.load("prompt/AI_Recommendations_Prompt.txt")
        self.migration_instruction = PromptLoader.load("prompt/Cloud_Migrations_Prompt.txt")

        # Cache setup
        self.ttl_seconds = int(cache_hours * 3600)
        self.cache_map = {
            "system": None,
            "migration": None
        }
        self.cache_created = {
            "system": False,
            "migration": False
        }

    def _load_cache(self, cache_key: str, instruction: str):
        """Create or reuse a cached system instruction."""
        display_name = f"{cache_key}_llm_cache_{int(time.time())}"
        try:
            cache = self.client.caches.create(
                model=self.llm_model_name,
                config=types.CreateCachedContentConfig(
                    display_name=display_name,
                    system_instruction=instruction,
                    contents=[instruction],
                    ttl=f"{self.ttl_seconds}s"
                )
            )
            self.cache_map[cache_key] = cache
            self.cache_created[cache_key] = True
            print(f"[Cache:{cache_key}] Created: {cache.name} (expires in {self.ttl_seconds / 3600:.1f}h)")
        except Exception as e:
            raise RuntimeError(f"Failed to create {cache_key} cache: {e}")

    def _extend_cache(self, cache_key: str, additional_hours: float = 1):
        """Extend existing cache TTL."""
        if not self.cache_created[cache_key]:
            raise RuntimeError(f"No {cache_key} cache to extend.")
        new_ttl = int(additional_hours * 3600)
        try:
            self.client.caches.update(
                name=self.cache_map[cache_key].name,
                config=types.UpdateCachedContentConfig(ttl=f"{new_ttl}s")
            )
            self.ttl_seconds = new_ttl
            print(f"[Cache:{cache_key}] Extended by {additional_hours}h")
        except Exception as e:
            raise RuntimeError(f"Failed to extend {cache_key} cache: {e}")

    def _generate_response(self, final_data: Dict, cache_key: str, instruction: str) -> str:
        # Load and extend context cache
        self._load_cache(cache_key, instruction)
        self._extend_cache(cache_key)

        try:
            start = time.time()
            stream_response = self.client.models.generate_content_stream(
                model=self.llm_model_name,
                config=types.GenerateContentConfig(
                    cached_content=self.cache_map[cache_key].name,
                    temperature=0.2
                ),
                contents=final_data,
            )

            response_text = ""
            for chunk in stream_response:
                if hasattr(chunk, "text"):
                    print(chunk.text, end="", flush=True)
                    response_text += chunk.text
            duration = time.time() - start
            print(f"\n[Done in {duration:.2f}s]")
            return response_text

        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}") from e

    def llm_query(self, final_data: Dict) -> str:
        return self._generate_response(final_data, "system", self.system_instruction)

    def migration_query(self, final_migration_data: Dict) -> str:
        return self._generate_response(final_migration_data, "migration", self.migration_instruction)
