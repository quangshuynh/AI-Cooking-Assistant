import ast
import re
import sys
import os
import time
import json
import requests

start_time = time.time()

url = '129.21.42.90'
default_model = 'dolphin-llama3'
STEPS = 0
PROGRESS = 0

current_dir = os.path.dirname(os.path.abspath(__file__))
system_prompt_path = os.path.join(current_dir, 'system_prompt')
system_prompt2_path = os.path.join(current_dir, 'system_prompt2')


def ollama_chat(model: str, messages: list, host: str = "http://192.168.1.100:11434") -> dict:
    """
    Replacement for ollama.chat that uses requests to connect to a remote Ollama instance

    Args:
        model (str): Name of the model to use
        messages (list): List of message dictionaries with 'role' and 'content'
        host (str): Host URL of the Ollama instance

    Returns:
        dict: Response dictionary with the same structure as ollama.chat
    """
    try:
        response = requests.post(
            f"{host}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False  # This tells Ollama to return a single response
            },
            stream=False
        )
        response.raise_for_status()

        # Parse the single JSON response
        data = response.json()
        return {
            "message": {
                "content": data["message"]["content"]
            }
        }
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return {"message": {"content": ""}}
    except json.JSONDecodeError as e:
        print(f"Error parsing Ollama response: {e}")
        return {"message": {"content": ""}}

# Function to extract recipe content from XML-like or formatted content
def extract_recipe(xml_content, pattern):
    match = re.search(pattern, xml_content, re.DOTALL)
    if not match:
        return None
    found_str = match.group(1)
    found_result = re.sub(r'\s+', ' ', found_str).strip()
    return found_result


# Function to parse a list of recipes from content
def parse_recipe_list(xml_content):
    try:
        dict_strs = extract_recipe(xml_content, r'<final_output>([\s\S]*?)</final_output>')
        recipe_list = []
        for dict_single in ast.literal_eval(dict_strs):
            recipe_list.append(dict_single)
    except:
        try:
            dict_strs = extract_recipe(xml_content, r'python([\s\S] * ?)')
            recipe_list = []
            for dict_single in ast.literal_eval(dict_strs):
                recipe_list.append(dict_single)
        except:
            try:
                dict_strs = extract_recipe(xml_content, r'([\s\S] * ?)')
                recipe_list = []
                for dict_single in ast.literal_eval(dict_strs):
                    recipe_list.append(dict_single)
            except:
                try:
                    dict_strs = '[' + extract_recipe(xml_content, r'\[(.*?)\]') + ']'
                    recipe_list = []
                    for dict_single in ast.literal_eval(dict_strs):
                        recipe_list.append(dict_single)
                except:
                    return None
    return recipe_list


# Optional: Convert the extracted content into an actual dictionary
def parse_recipe_dict(xml_content):
    dict_str = extract_recipe(xml_content, r'<final_output>\s*({[\s\S]*?})\s*</final_output>')
    if dict_str:
        try:
            return eval(dict_str)  # Caution: Use eval() only with trusted input
        except:
            return None
    return None


# Function to create a recipe dictionary
def write_recipe(name: str, description: str, ingredients: list[str] = None, cost: int = 0, cuisine: str = None,
                 serving_size: int = 0, meal_type: str = None,
                 allergies=None, diet: str = None) -> dict[str, str]:
    if allergies is None:
        allergies = ['None']

    with open(system_prompt_path, 'r') as f:
        system_prompt = {'role': 'system', 'content': str(f.read())}

    user_prompt = {'role': 'user', 'content': f"Recipe Name: {name}; "
                                              f"Description: {description}; "
                                              f"{'Requested Ingredients: ' + ', '.join(ingredients) if ingredients else 'No specific ingredient provided'}; "
                                              f"{'Cost $: ' + str(cost) + '; ' if cost > 0 else ''}"
                                              f"{'Cuisine type: ' + cuisine + '; ' if cuisine else ''}"
                                              f"{'Serving size: ' + str(serving_size) + '; ' if serving_size > 0 else ''}"
                                              f"{'Meal type: ' + meal_type + '; ' if meal_type else ''}"
                                              f"{'Allergies: ' + ', '.join(allergies) + '; ' if allergies else ''}"
                                              f"{'Diet: ' + diet + '; ' if diet else ''}"}

    count = 0
    while count < 10:
        count += 1
        global STEPS
        STEPS += 1
        response = ollama_chat(
            model=default_model,
            messages=[system_prompt, user_prompt],
            host=f"http://{url}:11434"  # Replace with your target IP
        )['message']['content']

        try:
            recipe_dict = parse_recipe_dict(response)
            assert type(recipe_dict) == dict
            assert type(recipe_dict['ingredients']) is list
            assert type(recipe_dict['instructions']) is list
            return recipe_dict
        except Exception as e:
            pass

    return False


# Function to create a list of recipes
def create_recipe_list(ingredients: list[str] = None, cost: int = 0, cuisine: str = None, serving_size: int = 0,
                       meal_type: str = None,
                       allergies=None, diet: str = None) -> list[dict[str, str]]:
    if allergies is None:
        allergies = ['None']

    with open(system_prompt2_path, 'r') as f:
        system_prompt = {'role': 'system', 'content': str(f.read())}

    # Capture ingredients passed from Flask as a list of strings
    user_prompt = {'role': 'user', 'content': f"The ingredients are: {', '.join(ingredients)}; "
                                              f"{'Cost $: ' + str(cost) + '; ' if cost > 0 else ''}"
                                              f"{'Cuisine type: ' + cuisine + '; ' if cuisine else ''}"
                                              f"{'Serving size: ' + str(serving_size) + '; ' if serving_size > 0 else ''}"
                                              f"{'Meal type: ' + meal_type + '; ' if meal_type else ''}"
                                              f"{'Allergies: ' + ', '.join(allergies) + '; ' if allergies else ''}"
                                              f"{'Diet: ' + diet + '; ' if diet else ''}"}

    count = 0
    while count < 10:
        count += 1
        global STEPS
        STEPS += 1

        response = ollama_chat(
            model=default_model,
            messages=[system_prompt, user_prompt],
            host=f"http://{url}:11434"  # Replace with your target IP
        )['message']['content']

        try:
            recipe_list_dict = parse_recipe_list(response)
            assert type(recipe_list_dict) is list
            assert type(recipe_list_dict[0]) is dict
            assert type(recipe_list_dict[0]['recipe']) is str
            assert type(recipe_list_dict[0]['description']) is str

            return recipe_list_dict
        except Exception as e:
            pass

    return []


if __name__ == "__main__":
    print("This module should be imported, not run directly")
