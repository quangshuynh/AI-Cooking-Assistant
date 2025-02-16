import os
import requests
from typing import List, Dict
from .base_model import BaseModel

class OllamaModel(BaseModel):
    def __init__(self):
        default_host = 'http://localhost:11434'
        host = os.getenv('OLLAMA_HOST', default_host)
        # Ensure URL has scheme
        if not host.startswith(('http://', 'https://')):
            host = 'http://' + host
        self.host = host.rstrip('/')
        self.model = os.getenv('OLLAMA_MODEL', 'dolphin-llama3')

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            # Ensure URL is properly formatted
            chat_url = f"{self.host}/api/chat"
            print(f"Attempting to connect to Ollama at: {chat_url}")
            print(f"Using model: {self.model}")
            
            try:
                # First check if model is available
                response = requests.get(f"{self.host}/api/tags")
                response.raise_for_status()
                available_models = [model['name'] for model in response.json()['models']]
                if self.model not in available_models:
                    print(f"Model {self.model} not found. Available models: {available_models}")
                    return ""
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
