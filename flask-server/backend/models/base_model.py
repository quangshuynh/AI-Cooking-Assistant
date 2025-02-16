from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseModel(ABC):
    """Base class for all language models"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send a chat request to the model
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: Model's response text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and properly configured"""
        pass
