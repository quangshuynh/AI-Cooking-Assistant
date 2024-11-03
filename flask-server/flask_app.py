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
    selected_ingredients = data.get('ingredients', [])
    
    recipe = run_llm(selected_ingredients)  # call LLM.py with the selected ingredients and get the result
    
    return jsonify({"recipe": recipe})

def run_llm(ingredients):
    try:
        # example of calling LLM.py script and passing ingredients
        result = subprocess.run([sys.executable, 'BackEnd-Stuff/LLM.py'] + ingredients, capture_output=True, text=True
        )
        
        if result.returncode != 0:  # check if there is any error during execution
            return f"Error generating recipe: {result.stderr}"
        
        return result.stdout
    except Exception as e:
        return f"Exception while generating recipe: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
