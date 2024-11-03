from recipe_vector_DB import RecipeDB, get_recipes_by_ingredients

if __name__ == "__main__":
    db = RecipeDB()

    # Test the collection first
    print("\nTesting collection content:")
    db.test_collection_content()

    print("\nStarting search interface:")
    while True:
        user_input = input('\nEnter ingredients (or "quit" to exit): ')
        if user_input.lower() == 'quit':
            break

        recipes = get_recipes_by_ingredients(user_input, db)
        if not recipes:
            print("\nNo matching recipes found. Try different ingredients.")
            continue

        print("\nMatching Recipes:")
        for recipe in recipes:
            print(f"\nTitle: {recipe['title']}")
            print(f"Similarity Score: {recipe['similarity_score']:.4f}")

            ingredients = recipe.get('ingredients', 'No ingredients available')
            instructions = recipe.get('instructions', 'No instructions available')

            if ingredients:
                print("Ingredients:", ingredients[:200] + "..." if len(ingredients) > 200 else ingredients)
            if instructions:
                print("Instructions:", instructions[:200] + "..." if len(instructions) > 200 else instructions)
            print("-" * 80)