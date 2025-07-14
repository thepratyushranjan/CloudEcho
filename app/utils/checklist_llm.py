# -*- coding: utf-8 -*-

import os
import json
import re
import requests
from config.config import Config
from typing import Dict, Any, List, Union


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

class ChecklistLlmGenerator:
    def __init__(self, llm_model_name: str = "gemma3n:e4b", url: str = "http://host.docker.internal:11434/api/generate"):
        self.url = url
        self.llm_model_name = llm_model_name
        # Load prompts from files
        self.overview_system_instruction = PromptLoader.load("prompt/checklist/AI_Checklist_Overview_Prompt.txt")
        self.cost_control_system_instruction = PromptLoader.load("prompt/checklist/AI_Checklist_Cost_Controls_Prompt.txt")
        self.usage_and_forecast_system_instruction = PromptLoader.load("prompt/checklist/AI_Checklist_Forecast_prompt.txt")
        self.security_system_instruction = PromptLoader.load("prompt/checklist/AI_Checklist_Security_Prompt.txt")
        self.applied_rules_system_instruction = PromptLoader.load("prompt/checklist/AI_Checklist_Applied_Rules_Prompt.txt")
        self.meta_tag_system_instruction = PromptLoader.load("prompt/checklist/AI_Checklist_Meta_Tag_Prompt.txt")

    def _generate_response(self, transform_content: str, system_instruction: str, temperature: float) -> str:
        """General method to generate a response from the API."""
        try:
            data = {
                "model": self.llm_model_name,
                "prompt": f"""{transform_content}\n{system_instruction}""",
                "stream": False,
                "temperature": temperature,
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(self.url, headers=headers, json=data)
            response_data = response.json()
            response_content = response_data.get('response', {})
            return response_content
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")
    
    def generate_overview_response(self, transform_content: str, temperature: float = 0.9) -> str:
        """Generate response for overview query."""
        return self._generate_response(transform_content, self.overview_system_instruction, temperature)

    def generate_cost_control_response(self, transform_content: str, temperature: float = 0.9) -> str:
        """Generate response for cost control query."""
        return self._generate_response(transform_content, self.cost_control_system_instruction, temperature)
    
    def generate_usage_and_forecast_response(self, transform_content: str, temperature: float = 0.9) -> str:
        return self._generate_response(transform_content, self.usage_and_forecast_system_instruction, temperature)
    
    def generate_security_query_response(self, transform_content: str, temperature: float = 0.9) -> str:
        return self._generate_response(transform_content, self.security_system_instruction, temperature)
    
    def generate_applied_rules_response(self, transform_content: str, temperature: float = 0.9) -> str:
        return self._generate_response(transform_content, self.applied_rules_system_instruction, temperature)
    
    def generate_meta_tag_query_response(self, transform_content: str, temperature: float = 0.9) -> str:
        return self._generate_response(transform_content, self.meta_tag_system_instruction, temperature)
    def overview_query(self, transform_content: str) -> str:
        """Overview query method."""
        return self.generate_overview_response(transform_content)
    
    def cost_control_query(self, transform_content: str) -> str:
        """Cost control query method."""
        return self.generate_cost_control_response(transform_content)
    
    def usage_and_forecast_query(self, transform_content: str) -> str:
        return self.generate_usage_and_forecast_response(transform_content)
    
    def security_query(self, transform_content: str) -> str:
        return self.generate_security_query_response(transform_content)

    def applied_rules(self, transform_content: str) -> str:
        return self.generate_applied_rules_response(transform_content)
    
    def meta_tag_query(self, transform_content: str) -> str:
        return self.generate_meta_tag_query_response(transform_content)
    
    

# Json Formatter
def extract_json_from_codeblock(s):
    match = re.search(r"```json\s*(.*?)\s*```", s, re.DOTALL)
    if match:
        return match.group(1)
    return s

def merge_codeblock_jsons(response1, response2, response3, response4, response5, response6) -> str:
    json1 = extract_json_from_codeblock(response1)
    json2 = extract_json_from_codeblock(response2)
    json3 = extract_json_from_codeblock(response3)
    json4 = extract_json_from_codeblock(response4)
    json5 = extract_json_from_codeblock(response5)
    json6 = extract_json_from_codeblock(response6)
    list1 = json.loads(json1)
    list2 = json.loads(json2)
    list3 = json.loads(json3)
    list4 = json.loads(json4)
    list5 = json.loads(json5)
    list6 = json.loads(json6)
    merged_list = list1 + list2 + list3 + list4 + list5 + list6
    return json.dumps(merged_list, indent=2)




