import os
from typing import Optional
from .base_model import BaseModel
from .ollama_model import OllamaModel
from .anthropic_model import AnthropicModel

class ModelFactory:
    @staticmethod
    def create_model(provider: Optional[str] = None) -> BaseModel:
        """
        Create and return a model instance based on the provider
        
        Args:
            provider: Model provider name (ollama, anthropic)
                     If None, uses DEFAULT_MODEL_PROVIDER from env
        
        Returns:
            BaseModel: Instance of the requested model
        """
        if provider is None:
            provider = os.getenv('DEFAULT_MODEL_PROVIDER')
            if not provider:
                print("WARNING: DEFAULT_MODEL_PROVIDER not found in environment variables")
                provider = 'ollama'
            else:
                provider = provider.lower().strip()
            print(f"Using model provider: {provider}")
            print(f"Environment variables loaded: {dict(os.environ)}")

        provider = provider.lower()
        if provider == 'ollama':
            return OllamaModel()
        elif provider == 'anthropic':
            return AnthropicModel()
        else:
            raise ValueError(f"Unknown model provider: {provider}")
