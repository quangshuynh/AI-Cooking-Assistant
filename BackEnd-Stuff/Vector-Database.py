# In your main script or notebook
from weaviate_ingredients import IngredientsDB

# Initialize the database
db = IngredientsDB()

# Search for similar ingredients
ingredient_to_search = input('Ingredient: ')
similar_ingredients = db.search_similar_ingredients_by_name(ingredient_to_search, limit=5)

# Print results
print(f"\nTop similar ingredients to '{ingredient_to_search}':")
for item in similar_ingredients:
    print(f"\nIngredient: {item['ingredient']}")
    print(f"Class: {item['class']}")
    print(f"Similarity Score: {item['similarity_score']:.4f}")