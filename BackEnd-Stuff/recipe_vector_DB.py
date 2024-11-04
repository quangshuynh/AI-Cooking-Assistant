import weaviate
from weaviate.classes import config as wvcc
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.filters import Filter
import pandas as pd
import yaml
from typing import Dict, List, Any
import atexit

class RecipeDB:
    def __init__(self, collection_name="Recipe", schema_path="schema2.yaml"):
        self.client = weaviate.connect_to_local()
        self.collection_name = collection_name
        self.schema_path = schema_path
        atexit.register(self.close)

        # First, check if we need to create or recreate the collection
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists and is properly initialized."""
        try:
            # Try to delete existing collection if it exists
            try:
                self.client.collections.delete(self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except Exception:
                pass

            # Create new collection
            print("Creating new collection...")
            self._create_collection_from_schema()

            # Initialize with data
            print("Initializing with data...")
            self._initialize_from_huggingface()

            # Verify collection exists
            self.collection = self.client.collections.get(self.collection_name)
            count = self.collection.aggregate.over_all(total_count=True).total_count
            print(f"Collection initialized with {count} recipes")

        except Exception as e:
            print(f"Error ensuring collection: {e}")
            raise

    def _create_collection_from_schema(self):
        try:
            # Load and print schema for debugging
            with open(self.schema_path, 'r') as file:
                schema = yaml.safe_load(file)
            print(f"Loaded schema: {schema}")

            properties = [
                wvcc.Property(
                    name=prop['name'],
                    data_type=wvcc.DataType.TEXT
                ) for prop in schema['properties']
            ]

            # Create collection with explicit configuration
            self.collection = self.client.collections.create(
                name=self.collection_name,
                vectorizer_config=wvcc.Configure.Vectorizer.text2vec_transformers(),
                properties=properties
            )
            print(f"Created collection {self.collection_name} with {len(properties)} properties")

        except Exception as e:
            print(f"Error creating collection: {e}")
            import traceback
            traceback.print_exc()
            raise

    def close(self):
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

    def batch_import_recipes(self, recipes_list: List[Dict[str, Any]]) -> bool:
        try:
            total = len(recipes_list)
            batch_size = 100
            batches = (total + batch_size - 1) // batch_size

            print(f"\nImporting {total} recipes in {batches} batches:")

            for batch_num in range(batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total)

                with self.collection.batch.dynamic() as batch:
                    for recipe in recipes_list[start_idx:end_idx]:
                        cleaned_recipe = {
                            'title': str(recipe.get('Title', '')),
                            'ingredients': str(recipe.get('Ingredients', '')),
                            'instructions': str(recipe.get('Instructions', ''))
                        }
                        # Only add recipe if it has all required fields
                        if all(cleaned_recipe.values()):
                            batch.add_object(properties=cleaned_recipe)

                print(f"\rProgress: {((batch_num + 1) / batches * 100):.1f}% ({end_idx}/{total} recipes)", end='',
                      flush=True)

            print("\nImport completed!")
            return True

        except Exception as e:
            print(f"\nError in batch import: {e}")
            return False

    def _initialize_from_huggingface(self):
        try:
            print("Loading data from dataset...")
            df = pd.read_csv(
                "hf://datasets/Hieu-Pham/kaggle_food_recipes/Food Ingredients and Recipe Dataset with Image Name Mapping.csv")
            print(f"Loaded {len(df)} records")

            # Clean the data
            df = df.fillna('')

            # Drop the unnamed index column if it exists
            if 'Unnamed: 0' in df.columns:
                df = df.drop('Unnamed: 0', axis=1)

            recipes_list = df.to_dict('records')

            # Print sample data for debugging
            print("\nSample recipe data:")
            print(recipes_list[0])

            success = self.batch_import_recipes(recipes_list)
            if success:
                print(f"Successfully imported {len(recipes_list)} recipes")
            else:
                print("Failed to import recipes")

        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            raise

    def search_similar_recipes_by_ingredients(self, ingredients: str, limit: int = 5) -> List[Dict]:
        """Search for recipes based on ingredients."""
        try:
            response = self.collection.query.near_text(
                query=ingredients,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    recipe = {
                        "title": obj.properties.get("title", "Untitled"),
                        "ingredients": obj.properties.get("ingredients", ""),
                        "instructions": obj.properties.get("instructions", ""),
                        "similarity_score": 1 - getattr(obj.metadata, 'distance', 0)
                    }
                    results.append(recipe)

            return sorted(results, key=lambda x: x['similarity_score'], reverse=True)

        except Exception as e:
            print(f"Error in recipe search: {e}")
            return []

def get_similar_recipes(ingredients, db=None):
    """Get recipes that match the given ingredients."""
    if db is None:
        db = RecipeDB()

    recipes = db.search_similar_recipes_by_ingredients(ingredients, limit=5)
    return [(recipe['title'],
             recipe['ingredients'][:200] + "..." if len(recipe['ingredients']) > 200 else recipe['ingredients'])
            for recipe in recipes]


if __name__ == '__main__':
    print("Initializing recipe database...")
    db = RecipeDB()

    while True:
        user_input = input('\nEnter ingredients (or "quit" to exit): ')
        if user_input.lower() == 'quit':
            break

        recipes = get_similar_recipes(user_input, db=db)
        if recipes:
            print("\nMatching Recipes:")
            for title, ingredients in recipes:
                print(f"\nTitle: {title}")
                print(f"Ingredients: {ingredients}")
        else:
            print("No matching recipes found. Try different ingredients.")