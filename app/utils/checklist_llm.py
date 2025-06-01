# -*- coding: utf-8 -*-

from google import genai
from google.genai import types
from config.config import Config
import os

class ChecklistLlmGenerator:
    def __init__(self, llm_model_name: str = "gemini-2.0-flash"):
        self.llm_model_name = llm_model_name
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.system_instruction = read_system_instruction()
    
    def generate_query_response(self, final_data: dict):
        try:
            stream_response = self.client.models.generate_content_stream(
                model=self.llm_model_name,
                config=types.GenerateContentConfig(system_instruction=self.system_instruction),
                contents=final_data,
            )
            
            response_text = ""
            for chunk in stream_response:
                if hasattr(chunk, "text"):
                    print(chunk.text, end="")
                    response_text += chunk.text
            return response_text
        except Exception as e:
            raise Exception(f"Error generating response for combined prompt: {e}")

    def llm_query(self, final_data: dict) -> str:
        return self.generate_query_response(final_data)


def read_system_instruction(file_path: str = "prompt/AI_Checklist_Prompt.txt") -> str:
    file_path = os.path.abspath(file_path)
    try:
        with open(file_path, "r") as file:
            prompt_content = file.read().strip()
        return prompt_content
    except FileNotFoundError:
        raise Exception(f"Prompt file '{file_path}' not found.")

