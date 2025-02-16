# AI Cooking Assistant

An intelligent recipe generation application that creates personalized recipes based on your available ingredients.

## Features
- Ingredient-based recipe generation with category organization
- Multiple AI model support (Ollama, Anthropic Claude)
- Dark/Light theme support
- Comprehensive filtering system:
  - Allergies and dietary restrictions
  - Cuisine types
  - Meal categories
  - Budget constraints
  - Serving size adjustments
- Interactive ingredient search and selection
- Real-time recipe generation
- Support for both recipe generation and existing recipe search

## Technologies Used
- **Backend:** Flask, Python
- **Frontend:** HTML, CSS, JavaScript
- **AI Models:** 
  - Ollama (local)
  - Anthropic Claude (API)
- **Database:** Weaviate (for recipe similarity searches)
- **Deployment:** Docker

## Installation

### Prerequisites
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
   git clone https://github.com/quangshuynh/AI-Cooking-Assistant.git
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

4. Create a `.env` file in the project root:

   ##### Ollama:
   ```env
   DEFAULT_MODEL_PROVIDER=ollama

   # Ollama Settings 
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=dolphin-llama3
   ```

   ##### Anthropic Claude:
   ```env
   DEFAULT_MODEL_PROVIDER=anthropic

   # Anthropic Settings
   ANTHROPIC_API_KEY=your-api-key-here
   ANTHROPIC_MODEL=claude-3-opus-20240229
   ```

5. Run the Flask server:
   ```sh
   python flask-server/flask_app.py
   ```

6. Open a browser and navigate to:
   ```
   http://127.0.0.1:5000/

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

## AI Model Configuration\
### Ollama
- Default local model option
- Requires Ollama to be installed and running
- No API key needed
- Configure host and model name in .env

### Anthropic Claude
- Cloud-based option
- Requires Anthropic API key
- Supports all Claude models
- Configure API key and model name in .env

## Adding New AI Models

The application uses a modular model system. To add a new AI provider:

1. Create a new model class in `backend/models/`
2. Inherit from `BaseModel`
3. Implement required methods:
   - `chat()`: Handle message exchange
   - `is_available()`: Check configuration
4. Add the model to `ModelFactory`

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
