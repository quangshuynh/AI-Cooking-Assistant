from flask import Flask, render_template, request, jsonify
import jinja2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.ingredient_db_efficient import IngredientDBEfficient
from backend.recipe_vector_DB import RecipeDB

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)

# Initialize databases
ingredient_db = IngredientDBEfficient()
recipe_db = RecipeDB()


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/suggest_ingredients')
def suggest_ingredients():
    query = request.args.get('query', '')
    if not query.strip():
        return jsonify([])

    try:
        # Use the initialized database instance
        similar_ingredients = ingredient_db.search_similar_ingredients(query, limit=5)
        # Add the search query as first suggestion if no exact match exists
        suggestions = []
        query_capitalized = ' '.join(word.capitalize() for word in query.strip().split())
        
        # Extract ingredient names from results
        result_ingredients = []
        for item in similar_ingredients:
            if isinstance(item, dict) and 'properties' in item:
                ingredient = item['properties'].get('ingredient')
                if ingredient:
                    result_ingredients.append(ingredient.lower())
        
        # Add search query first if it's not in results
        if query.lower() not in result_ingredients:
            suggestions.append(query_capitalized)
        
        # Add other suggestions
        suggestions.extend(result_ingredients)
        return jsonify(suggestions)
    except Exception as e:
        print(f"Error suggesting ingredients: {e}")
        return jsonify([])


@app.route('/find_recipes', methods=['POST'])
def find_recipes():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400

        query = data.get('query', '')
        print(f"Searching recipes for: {query}")

        # Search recipes using the initialized database
        recipes = recipe_db.search_similar_recipes_by_ingredients(query, limit=3)
        
        if not recipes:
            return jsonify({'recipes': []})

        # Format the recipes for response
        formatted_recipes = []
        for recipe in recipes:
            try:
                # Handle ingredients parsing more safely
                ingredients = recipe.get('ingredients', '')
                if isinstance(ingredients, str):
                    try:
                        # Try to evaluate if it looks like a list literal
                        if ingredients.strip().startswith('[') and ingredients.strip().endswith(']'):
                            ingredients = eval(ingredients)
                        else:
                            # Split by commas and clean up each ingredient
                            ingredients = [i.strip() for i in ingredients.split(',') if i.strip()]
                    except Exception as e:
                        print(f"Error parsing ingredients: {e}")
                        ingredients = [ingredients]  # Keep as single item if parsing fails
                
                formatted_recipe = {
                    'title': recipe.get('title', 'Untitled Recipe'),
                    'ingredients': ingredients,
                    'instructions': recipe.get('instructions', 'No instructions available'),
                    'similarity': recipe.get('similarity_score', 0)
                }
                formatted_recipes.append(formatted_recipe)
            except Exception as e:
                print(f"Error formatting recipe: {e}")
                continue

        return jsonify({'recipes': formatted_recipes})

    except Exception as e:
        print(f"Error in find_recipes: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Get ingredients and ensure they're properly formatted
        ingredients = [ing.strip() for ing in data.get('ingredients', []) if ing.strip()]
        cuisine = data.get("cuisine", "")
        meal_type = data.get("meal_type", "")

        if not ingredients:
            return jsonify({"error": "No ingredients provided"}), 400

        # Import LLM functions
        from backend.LLM import create_recipe_list, write_recipe
        
        # Generate recipe list
        print(f"Generating recipes for ingredients: {ingredients}")
        recipes_list = create_recipe_list(
            ingredients=ingredients,
            cuisine=cuisine,
            meal_type=meal_type
        )

        if not recipes_list:
            return jsonify({"error": "No recipes could be generated"}), 404

        # Format each recipe
        formatted_recipes = []
        for recipe_info in recipes_list:
            try:
                recipe = write_recipe(
                    name=recipe_info['recipe'],
                    description=recipe_info['description'],
                    ingredients=ingredients,
                    cuisine=cuisine,
                    meal_type=meal_type
                )
                
                if recipe:
                    formatted_recipes.append({
                        "name": recipe_info['recipe'],
                        "description": recipe_info['description'],
                        "ingredients": recipe['ingredients'],
                        "instructions": recipe['instructions']
                    })
            except Exception as e:
                print(f"Error formatting recipe: {e}")
                continue

        if not formatted_recipes:
            return jsonify({"error": "Failed to format recipes"}), 500

        return jsonify({"recipes": formatted_recipes})

    except Exception as e:
        print(f"Error generating recipe: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
