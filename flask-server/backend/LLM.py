import ast
import re
import os
import time
from typing import List, Dict, Optional
from .models.model_factory import ModelFactory

start_time = time.time()
STEPS = 0
PROGRESS = 0

current_dir = os.path.dirname(os.path.abspath(__file__))
system_prompt_path = os.path.join(current_dir, 'system_prompt')
system_prompt2_path = os.path.join(current_dir, 'system_prompt2')

# Initialize the AI model
model = ModelFactory.create_model()

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
        
        response = model.chat([system_prompt, user_prompt])
        
        try:
            recipe_dict = parse_recipe_dict(response)
            assert isinstance(recipe_dict, dict)
            assert isinstance(recipe_dict['ingredients'], list)
            assert isinstance(recipe_dict['instructions'], list)
            return recipe_dict
        except Exception as e:
            print(f"Error parsing recipe: {e}")
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

        response = model.chat([system_prompt, user_prompt])

        try:
            recipe_list_dict = parse_recipe_list(response)
            assert isinstance(recipe_list_dict, list)
            assert isinstance(recipe_list_dict[0], dict)
            assert isinstance(recipe_list_dict[0]['recipe'], str)
            assert isinstance(recipe_list_dict[0]['description'], str)

            return recipe_list_dict
        except Exception as e:
            print(f"Error parsing recipe list: {e}")
            pass

    return []


if __name__ == "__main__":
    print("This module should be imported, not run directly")
