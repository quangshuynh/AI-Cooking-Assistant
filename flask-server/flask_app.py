from flask import Flask, render_template, request, jsonify
import jinja2
import os
import sys
import subprocess
from backend import ingredient_db_efficient
from backend.recipe_vector_DB import get_similar_recipes

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)
current_dir = os.path.dirname(os.path.abspath(__file__))
llm_path = os.path.join(current_dir, 'backend', 'LLM.py')

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/suggest_ingredients')
def suggest_ingredients():
    query = request.args.get('query', '')
    if not query.strip():
        return jsonify([])

    # Use your existing function to get similar ingredients
    similar_ingredients = ingredient_db_efficient.get_similar_ingredients(query)

    # Return the suggestions (limiting to 5 if needed)
    return jsonify(similar_ingredients[:5])

@app.route('/find_recipes', methods=['POST'])
def find_recipes():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400

        query = data.get('query', '')
        print(f"Received query: {query}")  # Debug print

        # Get recipes from your database
        recipes = get_similar_recipes(query)
        print(f"Found recipes: {recipes}")  # Debug print

        if not recipes:
            return jsonify({'recipes': []})

        # Ensure we have all required fields
        formatted_recipes = []
        for recipe in recipes[:3]:  # Only take top 3
            formatted_recipe = {
                'title': recipe.get('title', 'Untitled Recipe'),
                'ingredients': recipe.get('ingredients', 'No ingredients listed'),
                'instructions': recipe.get('instructions', 'No instructions available')
            }
            formatted_recipes.append(formatted_recipe)

        return jsonify({'recipes': formatted_recipes})

    except Exception as e:
        print(f"Error in find_recipes: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():
    data = request.get_json()
    selected_ingredients = data.get('ingredients', []) #debugging
    print("Ingredients: " + selected_ingredients)
    
    # run the LLM and capture the formatted HTML output
    recipe_html = run_llm(selected_ingredients)
    
    return jsonify({"recipe_html": recipe_html})


def run_llm(ingredients):
    try:
        ingredients_str = "The ingredients are: " + ", ".join(ingredients)
        result = subprocess.run([sys.executable, llm_path, ingredients_str], capture_output=True, text=True)
    

        if result.returncode != 0: 
            return f"Error generating recipe: {result.stderr}"
        
        return result.stdout  # return the recipe output
    except Exception as e:
        return f"Exception while generating recipe: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
