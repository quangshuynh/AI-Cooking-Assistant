import sys

import ollama

model = 'llava-llama3'

def get_ingredients(image):
    system_prompt = {'role': 'system', 'content': 'You are an ingredient analyzer. '
                                                  'You are given an image and must retrieve the ingredients from it.'
                                                  'You must output a python list.'
                                                  'Example: [ingredient1, ingredient2, ingredient3]'}

    user_prompt = {'role': 'user', 'content': 'Get the ingredients from this image.', 'images': image}

    response = ollama.chat(
        model=model,
        messages=[system_prompt, user_prompt]
    )['message']['content']

    return response

if __name__ == '__main__':
    print(get_ingredients('image1.jpg'))