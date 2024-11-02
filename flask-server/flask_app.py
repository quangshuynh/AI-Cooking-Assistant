from flask import Flask, request, jsonify
import pandas as pd
import jinja2
import os

csv_path = os.path.join(os.path.dirname(__file__), 'database', 'food.csv.gz')
data = pd.read_csv(csv_path, compression="gzip")
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)

@app.route('/api/ingredients', methods=['GET'])
def search_ingredients():
    query = request.args.get('query', '').lower()

    # filter by query in description (top 5 most relevant)
    if query:
        filtered_data = data[data['description'].fillna('').str.lower().str.contains(query)]
        top_results = filtered_data.head(5).to_dict(orient='records')
    else:
        top_results = []
    return jsonify(top_results)


@app.route('/api/recipes', methods=['GET'])
def generate_recipe():
    selected_ingredients = request.args.getlist('ingredients')
    allergies = request.args.get('allergies', '').split(',')
    max_cost = request.args.get('max_cost', None, type=float)
    cuisine = request.args.get('cuisine', '').lower()
    serving_size = request.args.get('serving_size', None, type=int)
    meal_type = request.args.get('meal_type', '').lower()

    # filter based on selected ingredients and other preferences
    filtered_data = data[data['description'].isin(selected_ingredients)]

    # apply filters if they are provided
    if max_cost:
        filtered_data = filtered_data[filtered_data.get('cost', 0) <= max_cost]
    if cuisine:
        filtered_data = filtered_data[filtered_data['cuisine'].str.lower() == cuisine]
    if meal_type:
        filtered_data = filtered_data[filtered_data['meal_type'].str.lower() == meal_type]

    # exclude any allergens
    for allergy in allergies:
        if allergy:
            filtered_data = filtered_data[~filtered_data['description'].str.contains(allergy, case=False)]

    results = filtered_data.to_dict(orient='records')
    return jsonify(results)


@app.route("/")
def home():
    template = jinja_env.get_template('index.html')
    return template.render()

if __name__ == "__main__":
    app.run(debug=True)

