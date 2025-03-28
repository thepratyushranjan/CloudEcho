from google import genai
from google.genai import types
from app.core.config import Config

class LlmGenerator:
    def __init__(self, llm_model_name="gemini-2.0-flash"):
        self.llm_model_name = llm_model_name
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)

    def generate_query_embedding(self, query: str, system_instruction: str = "Introduction of Cloudtuner.") -> list[float]:
        """
        Generates an embedding for a single query using the Gemini API.
        A constant system instruction is used by default.
        """
        try:
            response = self.client.models.generate_content(
                model=self.llm_model_name,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                ),
                contents=query
            )
            return response
        except Exception as e:
            raise Exception(f"Error generating embedding for query: {e}")

    def llm_query(self, text: str, system_instruction: str = "Introduction of Cloudtuner") -> list[float]:
        """Wraps generate_query_embedding for a single query."""
        return self.generate_query_embedding(text, system_instruction)


