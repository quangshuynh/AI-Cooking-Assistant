# AI Cooking Assistant

The AI Cooking Assistant is an intelligent recipe generator that allows users to create personalized recipes based on their available ingredients, dietary restrictions, budget, and cuisine preferences. It leverages AI and a database of recipes to generate or find meals tailored to user inputs.

## Features
- Ingredient-based recipe generation
- Allergy and dietary restriction filters
- Budget-conscious meal planning
- Cuisine-specific recommendations
- Meal type categorization (Breakfast, Lunch, Dinner)
- Interactive ingredient selection UI
- AI-powered recipe recommendations

## Technologies Used
- **Backend:** Flask, Python
- **Frontend:** HTML, CSS, JavaScript
- **Database:** Weaviate (for recipe similarity searches)
- **AI Model:** Ollama API (for generating recipes)
- **Deployment:** Docker (optional)

## Installation
### Prerequisites
Ensure you have the following installed:
- Ollama (`dolphin-llama3`)
- Python 3.8+
- Flask (`pip install flask`)
- Weaviate (`pip install weaviate-client`)
- Requests (`pip install requests`)
- Jinja2 (`pip install jinja2`)
- NumPy (`pip install numpy`)

### Setup Instructions
1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/ai-cooking-assistant.git
   cd ai-cooking-assistant
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Start the Weaviate database (optional, if using local vector search):
   ```sh
   weaviate --host localhost --port 8080
   ```

4. Run the Flask server:
   ```sh
   python flask-server/flask_app.py
   ```

5. Open a browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Deployment
### Docker (Optional)
To containerize the application, ensure you have Docker installed and follow these steps:
1. Build the Docker image:
   ```sh
   docker build -t ai-cooking-assistant .
   ```
2. Run the container:
   ```sh
   docker run -p 5000:5000 ai-cooking-assistant
   ```

## API Endpoints
### 1. Generate Recipe
- **Endpoint:** `/generate_recipe`
- **Method:** POST
- **Payload:**
  ```json
  {
    "ingredients": ["chicken", "garlic", "tomato"],
    "cuisine": "Italian",
    "meal_type": "Dinner"
  }
  ```
- **Response:**
  ```json
  {
    "recipe_html": "<div>Generated Recipe...</div>"
  }
  ```

### 2. Find Similar Recipes
- **Endpoint:** `/find_recipes`
- **Method:** POST
- **Payload:**
  ```json
  {
    "query": "chicken, garlic, tomato"
  }
  ```
- **Response:**
  ```json
  {
    "recipes": [
      {
        "title": "Garlic Chicken Pasta",
        "ingredients": "Chicken, Garlic, Tomato, Pasta, Olive Oil",
        "instructions": "Cook chicken..."
      }
    ]
  }
  ```

### 3. Ingredient Suggestions
- **Endpoint:** `/suggest_ingredients`
- **Method:** GET
- **Query Parameter:** `query=<ingredient>`
- **Response:**
  ```json
  ["Chicken", "Garlic", "Tomato"]
  ```

## Contributing
Contributions are welcome! Feel free to fork this project and submit a pull request with improvements or new features.

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

