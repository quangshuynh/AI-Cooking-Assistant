from flask import Flask
import jinja2
import os
# import pandas as pf


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
# df = pd.read_csv("hf://datasets/Hieu-Pham/kaggle_food_recipes/Food Ingredients and Recipe Dataset with Image Name Mapping.csv")

app = Flask(__name__)

@app.route("/")
def home():
    template = jinja_env.get_template('index.html')
    return template.render()

if __name__ == "__main__":
    app.run(debug=True)
