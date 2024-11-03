from flask import Flask, render_template, request, jsonify
import jinja2
import os
import sys
import subprocess


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():
    data = request.get_json()
    selected_ingredients = data.get('ingredients', []) #debugging
    print(selected_ingredients)
    
    # run the LLM and capture the formatted HTML output
    recipe_html = run_llm(selected_ingredients)
    
    return jsonify({"recipe_html": recipe_html})


def run_llm(ingredients):
    try:
        ingredients_str = "The ingredients are: " + ", ".join(ingredients)
        result = subprocess.run([sys.executable, 'BackEnd-Stuff/LLM.py', ingredients_str], capture_output=True, text=True)
    

        if result.returncode != 0: 
            return f"Error generating recipe: {result.stderr}"
        
        return result.stdout  # return the recipe output
    except Exception as e:
        return f"Exception while generating recipe: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
