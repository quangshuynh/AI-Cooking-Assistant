import ollama
import ast

# default_model = ollama.list()['models'][0]['name']
default_model = 'llama3.2:1b'

def get_recipes(ingredients: list[str], cost: int=0, cuisine: str=None, serving_size: int=0, meal_type: str=None,
                allergies=None, diet: str=None) -> list[dict[str, str]]:
    if allergies is None:
        allergies = ['None']

    count = 0

    system_prompt = {'role': 'system', 'content': "You are a chef trying to find recipes with the given criteria. "
                                                  "Write your response in a list of python dictionary format: "
                                                  "[{'recipe': '...', 'ingredients': ['...'], 'instructions': ['instruction1', 'instruction2', 'instruction3', ...]}, {...}, ...]."
                                                  "The dictionaries' keys must only be 'recipe', 'ingredients', and 'instructions' keys."
                                                  "Do not write anything else than the list of dictionary."
                                                  "Do not include anything else than the list, no comments, no backtick."
                                                  "Write all the required ingredients for the recipe."}

    user_prompt = {'role': 'user', 'content': f"Requested Ingredients: {', '.join(ingredients)}; "
                                              f"{'Cost $: ' + str(cost) + '; ' if cost > 0 else ''}"
                                              f"{'Cuisine type: ' + cuisine + '; ' if cuisine else ''}"
                                              f"{'Serving size: ' + str(serving_size) + '; ' if serving_size > 0 else ''}"
                                              f"{'Meal type: ' + meal_type + '; ' if meal_type else ''}"
                                              f"{'Allergies: ' + ', '.join(allergies) + '; ' if allergies else ''}"
                                              f"{'Diet: ' + diet + '; ' if diet else ''}"}

    while count<10:
        count += 1
        print(count)
        response = ollama.chat(
            model=default_model,
            messages=[system_prompt, user_prompt],
        )['message']['content']

        # print(response)

        try:
            response = ast.literal_eval(response)
            for recipe in response:
                name, ingredients, instructions = recipe.values()
                print(f"Recipe: {name}, Ingredients: {', '.join(ingredients)}, Instructions: {', '.join(instructions)}")
                return response
        except Exception as e:
            pass
    return False

get_recipes(['potato', 'curry', 'chicken', 'broth', 'bread sticks'], cost=5)