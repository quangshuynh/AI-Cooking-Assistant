import weaviate
from weaviate.classes import config as wvcc
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.filters import Filter
import pandas as pd
import yaml
from typing import Dict, List, Any
import atexit
import os
import pickle
import os.path


class IngredientsDB:
    def __init__(self, collection_name="RecipeIngredients", schema_path="schema.yaml",
                 cache_file="encoded_ingredients.pkl", csv_file="04_Recipe-Ingredients_Aliases.csv",
                 base_dir=None, force_recreate=False):
        # Set base directory for file operations
        self.base_dir = base_dir if base_dir else os.getcwd()
        self.client = weaviate.connect_to_local(host='129.21.42.90')
        self.collection_name = collection_name
        self.schema_path = schema_path
        self.cache_file = cache_file
        self.csv_file = csv_file
        atexit.register(self.close)

        # Convert all file paths to absolute paths
        self.cache_file = os.path.abspath(os.path.join(self.base_dir, cache_file))
        self.csv_file = os.path.abspath(os.path.join(self.base_dir, csv_file))
        self.schema_path = os.path.abspath(os.path.join(self.base_dir, schema_path))

        # Connect to Weaviate
        self.client = weaviate.connect_to_local(host='129.21.42.90')
        self.collection_name = collection_name

        # If force_recreate is True, delete the existing collection
        if force_recreate:
            self.delete_collection()

        # Check existing collections
        existing_collections = self.client.collections.list_all()
        print(f"Existing collections: {existing_collections}")

        try:
            if self.collection_name in existing_collections:
                self.collection = self.client.collections.get(self.collection_name)
                print(f"Connected to existing collection: {self.collection_name}")
                try:
                    # Check if collection is empty
                    count = self.collection.aggregate.over_all(total_count=True).total_count
                    if count == 0:
                        print("Collection is empty, initializing data...")
                        self._initialize_data()
                except Exception as e:
                    print(f"Error checking collection count: {e}")
                    print("Proceeding with initialization...")
                    self._initialize_data()
            else:
                print(f"Creating new collection: {self.collection_name}")
                self._create_collection_from_schema()
                self._initialize_data()

        except Exception as e:
            print(f"Error checking collection count: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _preprocess_ingredients(self, df: pd.DataFrame) -> List[str]:
        """Preprocess ingredients from the Aliased Ingredient Name column."""

        # Process each description
        ingredients = df['Aliased Ingredient Name'].dropna()
        processed_ingredients = [ing.strip().title() for ing in ingredients]

        # Remove duplicates using set
        unique_ingredients = list(set(processed_ingredients))
        return unique_ingredients

    def delete_collection(self):
        """Delete the collection if it exists."""
        try:
            if self.collection_name in self.client.collections.list_all():
                self.client.collections.delete(self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")

    def _create_collection_from_schema(self):
        """Create the Weaviate collection using schema."""
        try:
            with open(self.schema_path, 'r') as file:
                schema = yaml.safe_load(file)

            properties = [
                wvcc.Property(
                    name='ingredient',
                    data_type=wvcc.DataType.TEXT
                ),
                wvcc.Property(
                    name='original_text',
                    data_type=wvcc.DataType.TEXT
                )
            ]

            self.collection = self.client.collections.create(
                name=self.collection_name,
                vectorizer_config=wvcc.Configure.Vectorizer.text2vec_transformers(),
                properties=properties
            )
        except weaviate.exceptions.UnexpectedStatusCodeError as e:
            if "already exists" in str(e):
                self.collection = self.client.collections.get(self.collection_name)
            else:
                raise

    def _initialize_data(self):
        """Initialize the database with data, using cache if available."""
        if os.path.exists(self.cache_file):
            print("Loading encoded data from cache...")
            with open(self.cache_file, 'rb') as f:
                encoded_data = pickle.load(f)
        else:
            print("Processing and encoding new data...")
            # Read and preprocess CSV
            df = pd.read_csv(self.csv_file)
            ingredients = self._preprocess_ingredients(df)

            # Create data objects
            encoded_data = [
                {
                    'ingredient': ingredient,
                    'original_text': ingredient  # You might want to store original text too
                }
                for ingredient in ingredients
            ]

            # Cache the encoded data
            with open(self.cache_file, 'wb') as f:
                pickle.dump(encoded_data, f)

        # Import the data to Weaviate
        self.batch_import_ingredients(encoded_data)

    def batch_import_ingredients(self, ingredients_list: List[Dict[str, Any]]) -> bool:
        """Import a batch of ingredients into the database."""
        try:
            with self.collection.batch.dynamic() as batch:
                for ingredient in ingredients_list:
                    batch.add_object(properties=ingredient)
            return True
        except Exception as e:
            print(f"Error in batch import: {e}")
            return False

    def search_similar_ingredients(self, query_text: str, limit: int = 5) -> List[Dict]:
        """Search for similar ingredients using vector similarity."""
        try:
            response = self.collection.query.near_text(
                query=query_text.lower(),  # Convert query to lowercase to match preprocessing
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    results.append({
                        "ingredient": obj.properties.get("ingredient", ""),
                        "similarity": 1 - getattr(obj.metadata, 'distance', 0)
                    })
            return results
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []

    def get_all_ingredients(self) -> List[str]:
        """Get all ingredients in the database."""
        try:
            response = self.collection.query.fetch_objects(
                limit=10000  # Adjust based on your expected data size
            )

            ingredients = []
            if hasattr(response, 'objects'):
                ingredients = [obj.properties.get("ingredient", "")
                               for obj in response.objects]
            return sorted(ingredients)
        except Exception as e:
            print(f"Error fetching all ingredients: {e}")
            return []

    def close(self):
        """Close the database connection."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            print(f"Error closing connection: {e}")


def get_similar_ingredients(ingredient: str) -> List[str]:
    """Get similar ingredients for a given ingredient."""
    with IngredientsDB() as db:
        similar_ingredients = db.search_similar_ingredients(ingredient, limit=5)
        return [item['ingredient'] for item in similar_ingredients]



def get_cache_location():
    """Utility function to get the location of the cache file."""
    db = IngredientsDB()
    return db.cache_file


if __name__ == '__main__':
    # Initialize once
    db = IngredientsDB()

    # Print cache file location
    print(f"\nCache file location: {db.cache_file}")

    # Example: Print all unique ingredients
    print("\nAll ingredients in database:")
    all_ingredients = db.get_all_ingredients()
    print(f"Total unique ingredients: {len(all_ingredients)}")
    print("Sample of ingredients:", all_ingredients[:10])

    # Interactive search loop
    print("\nStarting interactive search...")
    while True:
        user_input = input('\nIngredient (or "quit" to exit): ')
        if user_input.lower() == 'quit':
            break

        similar = get_similar_ingredients(user_input, db=db)
        print("\nSimilar ingredients:")
        for ing in similar:
            print(f"- {ing}")