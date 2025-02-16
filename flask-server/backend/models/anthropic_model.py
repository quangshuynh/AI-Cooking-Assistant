import os
import anthropic
from typing import List, Dict
from .base_model import BaseModel

class AnthropicModel(BaseModel):
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
        print(f"Initialized Anthropic with model: {self.model}")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            # Convert messages to Anthropic format
            formatted_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    # Prepend system message to first user message
                    formatted_messages.append({
                        'role': 'user',
                        'content': f"System: {msg['content']}"
                    })
                else:
                    formatted_messages.append(msg)

            response = self.client.messages.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=4096
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error in Anthropic chat: {e}")
            return ""

    def is_available(self) -> bool:
        return bool(os.getenv('ANTHROPIC_API_KEY'))
