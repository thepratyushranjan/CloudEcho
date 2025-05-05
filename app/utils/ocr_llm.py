# -*- coding: utf-8 -*-

import base64
import io
import os
from google import genai
from google.genai import types
from config.config import Config
from PIL import Image
from utils import output_cleaner
import json


class OcrLlmGenerator:
    def __init__(self, llm_model_name: str = "gemini-2.0-flash", prompt_file: str = "tests/ocr_prompt_invoice.txt"):
        self.prompt_file = prompt_file
        self.llm_model_name = llm_model_name
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.system_instruction = read_system_instruction(prompt_file)

    def base64_to_pil_image(self, base64_string: str) -> Image.Image:
        image_data = base64.b64decode(base64_string)
        image_stream = io.BytesIO(image_data)
        return Image.open(image_stream)

    def generate_query_response(self, base64_image: str = None) -> str:
        try:
            # print("Generating response...", flush=True)
            # print(len(base64_image), flush=True)
            pil_image = self.base64_to_pil_image(base64_image)

            system_instructons = self.system_instruction

            # Print first 1000 characters of the system instruction
            # print("System instruction: ", system_instructons[0:1000], flush=True)

            # Making Call to LLM
            response = self.client.models.generate_content(model=self.llm_model_name, config=types.GenerateContentConfig(
        system_instruction=system_instructons), contents=[pil_image])

            #Response
            raw_response = response.text
            cleaned_response = output_cleaner.clean_output(raw_response)

            response_dict = json.loads(cleaned_response)

            # print("Response dict: ", type(response_dict), response_dict, flush=True)

            final_response = None

            if self.prompt_file == 'tests/ocr_prompt_invoice.txt':
                print('Calling finalize invoice output',flush=True)
                final_response = output_cleaner.finalize_invoice_output(response_dict)
            else:
                final_response = output_cleaner.finalize_output(response_dict)
            
            # print(response.text)
            return final_response

        except Exception as e:
            raise Exception(f"Error generating response: {e}")

    def llm_query(self, base64_image: str = None) -> str:
        return self.generate_query_response(base64_image=base64_image)


def read_system_instruction(file_path: str = "tests/ocr_prompt_invoice.txt") -> str:
    # print("Reading system instruction from file...",file_path, flush=True)
    file_path = os.path.abspath(file_path)
    try:

        with open(file_path, "r") as file:
            prompt_content = file.read().strip()
        return prompt_content
    except FileNotFoundError:
        raise Exception(f"Prompt file '{file_path}' not found.")

