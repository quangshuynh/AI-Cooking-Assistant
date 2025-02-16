import os
from typing import List, Dict
import ollama
from .base_model import BaseModel

class OllamaModel(BaseModel):
    def __init__(self):
        self.model = os.getenv('OLLAMA_MODEL', 'dolphin-llama3')
        print(f"Initialized Ollama with model: {self.model}")
        # Create Ollama client
        self.client = ollama

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            print(f"Using Ollama model: {self.model}")
            try:
                # First check if model is available
                models = self.client.list()
                print(f"Available models: {models}")
                
                if not any(self.model in model['name'] for model in models['models']):
                    print(f"Model {self.model} not found in available models")
                    return ""
                    
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    stream=False
                )
                return response['message']['content']
            except ConnectionError as e:
                print(f"Connection error with Ollama: {e}")
                print("Please ensure Ollama is running and accessible")
                return ""
            except Exception as e:
                print(f"Error in Ollama chat: {e}")
                return ""
        except Exception as e:
            print(f"Unexpected error in Ollama chat: {e}")
            return ""

    def is_available(self) -> bool:
        try:
            # List models to check if Ollama is running
            self.client.list()
            return True
        except:
            return False
