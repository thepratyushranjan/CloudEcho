# -*- coding: utf-8 -*-

import base64
import io
import mimetypes
import os
from google import genai
from google.genai import types
from google.genai.types import Part
from config.config import Config
from PIL import Image
from utils import output_cleaner
import json


class OcrLlmGenerator:
    def __init__(self, llm_model_name: str = "gemini-2.0-pro"):

        self.llm_model_name = llm_model_name
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.system_instruction = None
        # self.system_instruction = read_system_instruction(prompt_file)

    def base64_to_pil_image(self, base64_string: str) -> Image.Image:
        image_data = base64.b64decode(base64_string)
        image_stream = io.BytesIO(image_data)
        return Image.open(image_stream)

    def generate_query_response(self, text_prompt: str = "", base64_image: str = None, prompt_file: str ="" ) -> str:
        try:
            # print("Generating response...", flush=True)
            # print(len(base64_image), flush=True)
            pil_image = self.base64_to_pil_image(base64_image)

            # print(text_prompt, flush=True)

            # ❗ Correct format: list of strings and/or Part objects (not dicts)
            response = self.client.models.generate_content(model=self.llm_model_name, contents=[pil_image, text_prompt])
            raw_response = response.text
            cleaned_response = output_cleaner.clean_output(raw_response)

            # print(response.text,flush=True)
            # print("Cleaned response: ",type(cleaned_response) ,cleaned_response, flush=True)

            response_dict = json.loads(cleaned_response)

            # print("Response dict: ", type(response_dict), response_dict, flush=True)

            final_response = None

            if prompt_file == 'tests/ocr_prompt_invoice.txt':
                print('Calling finalize invoice output',flush=True)
                final_response = output_cleaner.finalize_invoice_output(response_dict)
            else:
                final_response = output_cleaner.finalize_output(response_dict)
            
            # print(response.text)
            return final_response

        except Exception as e:
            raise Exception(f"Error generating response: {e}")

    def llm_query(self, text_prompt: str = "", base64_image: str = None, mime_type: str = "image/png", prompt_file: str = None) -> str:
        system_info = read_system_instruction(prompt_file)
        text_prompt = system_info
        # print('Base64 length: ',len(base64_image), flush=True)
        return self.generate_query_response(text_prompt=text_prompt, base64_image=base64_image, prompt_file=prompt_file)


def read_system_instruction(file_path: str = "tests/ocr_prompt_invoice.txt") -> str:
    print("Reading system instruction from file...",file_path, flush=True)
    file_path = os.path.abspath(file_path)
    try:

        with open(file_path, "r") as file:
            prompt_content = file.read().strip()
        return prompt_content
    except FileNotFoundError:
        raise Exception(f"Prompt file '{file_path}' not found.")

