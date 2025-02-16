import os
import requests
from typing import List, Dict
from .base_model import BaseModel

class OllamaModel(BaseModel):
    def __init__(self):
        self.host = os.getenv('OLLAMA_HOST', 'http://localhost:11434').rstrip('/')
        self.model = os.getenv('OLLAMA_MODEL', 'dolphin-llama3')

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            # Ensure URL is properly formatted
            chat_url = f"{self.host}/api/chat"
            print(f"Attempting to connect to Ollama at: {chat_url}")
            
            try:
                response = requests.post(
                    chat_url,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    },
                    stream=False,
                    timeout=30  # Add timeout
                )
                response.raise_for_status()
                return response.json()["message"]["content"]
            except requests.exceptions.RequestException as e:
                print(f"Network error in Ollama chat: {e}")
                return ""
            except (KeyError, ValueError) as e:
                print(f"Error parsing Ollama response: {e}")
                return ""
        except Exception as e:
            print(f"Unexpected error in Ollama chat: {e}")
            return ""

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/version")
            return response.status_code == 200
        except:
            return False
