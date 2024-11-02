from langchain_ollama import OllamaLLM


#goal create AI prompt for recipe given prompt
def response_recipe(ingredients: list[str], cost: int = "all", cuisine: str = "all", serving_size: int = "all",
                    meal_type: str = "all", allergies: str = "None"):
    model = OllamaLLM(model="llama3.2:3b")
    ingredient_prompt = ""
    for i in range(len(ingredients)):
        ingredient_prompt += ingredients[i]
        ingredient_prompt += " "
    prompt = "Create three recipe with " + ingredient_prompt + "with "
    if cost == "all":
        prompt += "all cost range "
    else:
        prompt += str(cost)
        prompt += " dollars, "
    prompt += "of "
    if cuisine == all:
        prompt += "all types of cuisine "
    else:
        prompt += (cuisine + " cuisine, ")
    prompt += "of "
    if serving_size == "all":
        prompt += "all serving sizes, "
    else:
        prompt += str(serving_size)
        prompt += " serving size, "
    prompt += "that is for "
    if meal_type == "all":
        prompt += "either breakfast, lunch or dinner, "
    else:
        prompt += (meal_type + ", ")
    prompt += "avoid "
    if allergies == "None":
        prompt += "no allergies."
    else:
        prompt += allergies
    print(prompt)  #test

    result = model.invoke(prompt)
    print(result)

    #code goes here
    return result

response_recipe(["chicken", "corn", "fish", "corn flakes"], 30, "American")