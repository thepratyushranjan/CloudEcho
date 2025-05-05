# -*- coding: utf-8 -*-

from utils.ocr_llm import OcrLlmGenerator as LlmGenerator


class OcrService:
    def __init__(self, llm_model_name: str = "gemini-2.0-flash",ocr_type: str = None):
        prompt_mapping = {
            "invoice": "tests/ocr_prompt_invoice.txt",
            "passbook": "tests/ocr_prompt_passbook.txt",
            "electricity_bill": "tests/ocr_prompt_electricity_bill.txt"
        }

        self.prompt = prompt_mapping.get(ocr_type, "tests/ocr_prompt_invoice.txt")
        self.llm_model_name = llm_model_name
        self.llm_generator = LlmGenerator(llm_model_name=self.llm_model_name,prompt_file=self.prompt)

    def process_ocr(self, base64_string: str) -> str:
        """
        Process the OCR request and generate a response using the LLM.
        """

        try:
            # Here you would typically decode the base64 string and perform OCR processing
            # For demonstration, we will just use the base64 string as the prompt
            image_data = base64_string

            response = self.llm_generator.llm_query(base64_image=image_data)
            return response
        except Exception as e:
            print(e, flush=True)
            raise Exception(f"Error processing OCR request: {e}")
