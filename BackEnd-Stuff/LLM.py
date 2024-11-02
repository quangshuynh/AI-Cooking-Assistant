


#ignore these codes, here for reference for Kai to learn how to use ollama
import ollama
default_model = ollama.list()['models'][0]['name']

class Agent:
    def __init__(self, name: str, description: str, model=default_model):
        self.name = name
        self.description = description
        self.model = model
        self.history = [{'role': 'system', 'content': f"You are {name}, {description}."}]

    def add_message(self, message: str, role='assistant'):
        self.history.append({'role': role, 'content': message})

    def response(self, message: str):
        self.history.append({'role': 'user', 'content': message})
        response = ollama.chat(
            model=self.model,
            messages=self.history
        )
        self.history.append({'role': 'assistant', 'content': response['message']['content']})
        return response

    def get_output(self, message: str):
        response = ollama.chat(
            model=self.model,
            messages=self.history + [{'role': 'user', 'content': message}]
        )
        return response