from recipe_vector_DB import RecipeDB

# Initialize database with debug output
db = RecipeDB()

while True:
    # Search with diagnostic information
    ingredients = input('Ingredients (q to quit): ')
    if ingredients == 'q':
        break
    print(f"\nSearching for recipes with: {ingredients}")
    matching_recipes = db.search_similar_recipes_by_ingredients(ingredients, limit=5)

    # Print results with checks
    for recipe in matching_recipes:
        print(f"\n{'=' * 50}")
        print(f"Recipe: {recipe.get('title', 'No title')}")
        print(f"Similarity Score: {recipe.get('similarity_score', 0):.4f}")

        ingredients = recipe.get('ingredients', '')
        if ingredients:
            print(f"Ingredients: {ingredients[:200]}...")
        else:
            print("Ingredients: Not available")

        instructions = recipe.get('instructions', '')
        if instructions:
            print(f"Instructions: {instructions[:200]}...")
        else:
            print("Instructions: Not available")