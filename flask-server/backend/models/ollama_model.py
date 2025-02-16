import os
import requests
from typing import List, Dict
from .base_model import BaseModel

class OllamaModel(BaseModel):
    def __init__(self):
        self.host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'dolphin-llama3')

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                },
                stream=False
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            print(f"Error in Ollama chat: {e}")
            return ""

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/version")
            return response.status_code == 200
        except:
            return False
