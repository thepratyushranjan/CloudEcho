# -*- coding: utf-8 -*-

import os
import time
from google import genai
from google.genai import types
from config.config import Config


def read_system_instruction(file_path: str = "prompt/AI_Checklist_Prompt.txt") -> str:
    file_path = os.path.abspath(file_path)
    try:
        with open(file_path, "r") as file:
            prompt_content = file.read().strip()
        return prompt_content
    except FileNotFoundError:
        raise Exception(f"Prompt file '{file_path}' not found.")
class ChecklistLlmGenerator:
    def __init__(self, llm_model_name: str = "gemini-2.5-flash", cache_hours: float = 1):
        self.llm_model_name = llm_model_name
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.system_instruction = read_system_instruction()
        self.cache = None
        self.ttl_seconds = int(cache_hours * 3600)
        self.cache_created = False
    
    def load_cache(self):
        """Create a cached_content entry for our system instruction, or reuse existing."""
        display_name = f"llmgen_{self.llm_model_name}_{int(time.time())}"
        try:
            self.cache = self.client.caches.create(
                model=self.llm_model_name,
                config=types.CreateCachedContentConfig(
                    display_name=display_name,
                    system_instruction=self.system_instruction,
                    contents=[self.system_instruction],
                    ttl=f"{self.ttl_seconds}s",
                )
            )
            self.cache_created = True
            print(f"[Cache] created: {self.cache.name}, expires in {self.ttl_seconds/3600:.1f}h")
        except Exception as e:
            raise RuntimeError(f"Failed to create cache: {e}")
        
    def extend_cache(self, additional_hours: float = 1):
        """Extend existing cache TTL by additional_hours."""
        if not self.cache_created:
            raise RuntimeError("No cache to extend; call load_cache() first.")
        new_ttl = int(additional_hours * 3600)
        try:
            self.client.caches.update(
                name=self.cache.name,
                config=types.UpdateCachedContentConfig(
                    ttl=f"{new_ttl}s"
                )
            )
            self.ttl_seconds = new_ttl
            print(f"[Cache] extended by {additional_hours}h")
        except Exception as e:
            raise RuntimeError(f"Failed to extend cache: {e}")   

    def generate_query_response(self, final_data: dict, temperature: float = 0.2) -> str:
        """Stream a response, using the cache for the system instruction."""
        # Ensure cache exists (and log whether it's created or reused)
        self.load_cache()
        self.extend_cache()  # Optional: extend cache TTL if needed

        try:
            start = time.time()
            stream = self.client.models.generate_content_stream(
                model=self.llm_model_name,
                config=types.GenerateContentConfig(
                    cached_content=self.cache.name,
                    temperature=temperature
                ),
                contents=final_data,
            )

            response_text = ""
            for chunk in stream:
                if hasattr(chunk, "text"):
                    print(chunk.text, end="", flush=True)
                    response_text += chunk.text
            duration = time.time() - start
            print(f"\n[Done in {duration:.2f}s]")
            return response_text

        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")

    def llm_query(self, final_data: dict) -> str:
        return self.generate_query_response(final_data)




