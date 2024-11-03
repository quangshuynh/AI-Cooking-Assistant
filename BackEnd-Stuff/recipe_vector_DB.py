import weaviate
from weaviate.classes import config as wvcc
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.filters import Filter
import pandas as pd
import yaml
from typing import Dict, List, Any
import atexit


class RecipeDB:
    def __init__(self, collection_name="Recipes", schema_path="schema.yaml"):
        """Initialize connection and create collection if it doesn't exist."""
        self.client = weaviate.connect_to_local()
        self.collection_name = collection_name
        self.schema_path = schema_path
        atexit.register(self.close)

        self._delete_collection_if_exists()
        self._create_collection_from_schema()
        self._initialize_from_dataset()

    def _delete_collection_if_exists(self):
        try:
            self.client.collections.delete(self.collection_name)
            print(f"Deleted existing collection: {self.collection_name}")
        except Exception:
            pass

    def _create_collection_from_schema(self):
        """Create collection with schema for recipe data."""
        try:
            properties = [
                wvcc.Property(name="title", data_type=wvcc.DataType.TEXT),
                wvcc.Property(name="ingredients", data_type=wvcc.DataType.TEXT),
                wvcc.Property(name="instructions", data_type=wvcc.DataType.TEXT),
                wvcc.Property(name="image_name", data_type=wvcc.DataType.TEXT),
                wvcc.Property(name="cleaned_ingredients", data_type=wvcc.DataType.TEXT),
            ]

            self.collection = self.client.collections.create(
                name=self.collection_name,
                vectorizer_config=wvcc.Configure.Vectorizer.text2vec_transformers(),
                properties=properties
            )
            print(f"Created new collection: {self.collection_name}")

        except Exception as e:
            print(f"Error creating collection: {e}")
            raise

    def _initialize_from_dataset(self):
        """Initialize the database from the recipe dataset."""
        try:
            print("Loading data from dataset...")
            df = pd.read_csv(
                "hf://datasets/Hieu-Pham/kaggle_food_recipes/Food Ingredients and Recipe Dataset with Image Name Mapping.csv")
            print(f"Loaded {len(df)} records from dataset")

            # Debug print
            print("\nDataset columns:", df.columns.tolist())
            print("\nFirst row sample:")
            print(df.iloc[0].to_dict())

            recipes_list = df.to_dict('records')
            print(f"\nPrepared {len(recipes_list)} recipes for import")

            # Import with progress reporting
            success = self.batch_import_recipes(recipes_list)
            if success:
                print(f"Successfully imported {len(recipes_list)} recipes")
            else:
                print("Failed to import recipes")

            # Verify import
            total_count = self.collection.aggregate.over_all(
                total_count=True
            ).total_count
            print(f"\nTotal recipes in database: {total_count}")

        except Exception as e:
            print(f"Error loading data from dataset: {e}")
            import traceback
            traceback.print_exc()
            raise

    def batch_import_recipes(self, recipes_list: List[Dict[str, Any]]) -> bool:
        """Import recipes in batch."""
        try:
            with self.collection.batch.dynamic() as batch:
                for recipe in recipes_list:
                    cleaned_recipe = {
                        k: '' if pd.isna(v) else str(v)
                        for k, v in recipe.items()
                        if k in ['title', 'ingredients', 'instructions', 'image_name', 'cleaned_ingredients']
                    }
                    batch.add_object(properties=cleaned_recipe)
            return True
        except Exception as e:
            print(f"Error in batch import: {e}")
            return False

    def search_recipes_by_ingredients(self, ingredients: str, limit: int = 5) -> List[Dict]:
        """
        Search for recipes based on ingredients list.

        Args:
            ingredients: String of ingredients to search for
            limit: Maximum number of results to return

        Returns:
            List of similar recipes with their similarity scores
        """
        try:
            print(f"Searching for recipes with ingredients: {ingredients}")

            # Use cleaned_ingredients field for search
            response = self.collection.query.near_text(
                query=ingredients,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                print(f"Found {len(response.objects)} potential matches")
                for obj in response.objects:
                    # Debug print
                    print(f"\nProcessing object with properties:")
                    for key, value in obj.properties.items():
                        print(f"{key}: {value[:100] if value else None}")

                    # Add all recipes, even if some fields are missing
                    recipe = {
                        "title": obj.properties.get("title", "Unknown Title"),
                        "ingredients": obj.properties.get("cleaned_ingredients",
                                                          obj.properties.get("ingredients", "No ingredients listed")),
                        "instructions": obj.properties.get("instructions", "No instructions available"),
                        "similarity_score": 1 - getattr(obj.metadata, 'distance', 0)
                    }
                    results.append(recipe)
                    print(f"Added recipe: {recipe['title']}")
            else:
                print("No objects found in response")

            # Sort results by similarity score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results
        except Exception as e:
            print(f"Error in ingredient search: {e}")
            print(f"Response object attributes: {dir(response) if 'response' in locals() else 'No response'}")
            return []

    def get_recipe_details(self, recipe_title: str) -> Dict:
        """Get full details for a specific recipe by title."""
        try:
            filter_by_title = Filter.by_property("title") == recipe_title
            response = self.collection.query.fetch_objects(
                limit=1,
                filters=filter_by_title
            )

            if hasattr(response, 'objects') and len(response.objects) > 0:
                obj = response.objects[0]
                return {
                    "title": obj.properties.get("title", "Unknown Title"),
                    "ingredients": obj.properties.get("cleaned_ingredients",
                                                      obj.properties.get("ingredients", "No ingredients listed")),
                    "instructions": obj.properties.get("instructions", "No instructions available"),
                    "image_name": obj.properties.get("image_name", "No image available")
                }
            return {}
        except Exception as e:
            print(f"Error getting recipe details: {e}")
            return {}

    def close(self):
        """Close the client connection."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            print(f"Error closing connection: {e}")


def main():
    try:
        print("Initializing recipe database...")
        db = RecipeDB()

        # Example ingredient searches with diagnostic information
        test_ingredients = [
            "chicken garlic soy sauce",
            "flour sugar eggs butter"
        ]

        for ingredients in test_ingredients:
            print(f"\n{'=' * 50}")
            print(f"Searching for recipes with: {ingredients}")
            similar = db.search_recipes_by_ingredients(ingredients, limit=3)

            print(f"\nFound {len(similar)} matching recipes:")
            for recipe in similar:
                print(f"\nRecipe: {recipe['title']}")
                print(f"Similarity Score: {recipe['similarity_score']:.4f}")
                print(f"Ingredients: {recipe['ingredients'][:200] if recipe['ingredients'] else 'Not available'}...")
                print(f"Instructions: {recipe['instructions'][:200] if recipe['instructions'] else 'Not available'}...")

    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
