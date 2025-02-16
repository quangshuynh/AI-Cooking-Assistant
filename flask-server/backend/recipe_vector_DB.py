import weaviate
import yaml
from weaviate.classes import config as wvcc
from weaviate.classes.query import MetadataQuery
import pandas as pd
from typing import Dict, List, Any
import atexit
import os
import time


class RecipeDB:
    def __init__(self, collection_name="Recipe", schema_path="schema2.yaml", backup_path="backups"):
        try:
            self.client = weaviate.connect_to_local()
            self.collection_name = collection_name
            self.schema_path = schema_path
            self.backup_path = backup_path
            atexit.register(self.close)

        try:
            # First try to get existing collection
            try:
                self.collection = self.client.collections.get(self.collection_name)
                # Check if collection has data
                count = self.collection.aggregate.over_all(total_count=True).total_count
                if count > 0:
                    print(f"Connected to existing collection with {count} recipes")
                    return
                else:
                    print("Collection exists but is empty. Recreating...")
                    self.client.collections.delete(self.collection_name)
            except weaviate.exceptions.UnexpectedStatusCodeError:
                print("No existing collection found. Creating new one...")

            # Create new collection and initialize
            self._create_collection_from_schema()
            self._initialize_from_huggingface()

        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

    def _create_collection_from_schema(self):
        """Create collection with schema for recipe data."""
        try:
            with open(self.schema_path, 'r') as file:
                schema = yaml.safe_load(file)

            properties = [
                wvcc.Property(
                    name=prop['name'],
                    data_type=wvcc.DataType.TEXT
                ) for prop in schema['properties']
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

    def _initialize_from_huggingface(self):
        """Initialize the database from HuggingFace dataset."""
        try:
            print("Loading data from HuggingFace...")
            df = pd.read_csv(
                "hf://datasets/Hieu-Pham/kaggle_food_recipes/Food Ingredients and Recipe Dataset with Image Name Mapping.csv")

            total = len(df)
            batch_size = 100
            batches = (total + batch_size - 1) // batch_size

            print(f"\nImporting {total} recipes in {batches} batches:")

            for batch_num in range(batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total)

                with self.collection.batch.dynamic() as batch:
                    for _, recipe in df.iloc[start_idx:end_idx].iterrows():
                        cleaned_recipe = {
                            'title': str(recipe.get('Title', '')),
                            'ingredients': str(recipe.get('Ingredients', '')),
                            'instructions': str(recipe.get('Instructions', ''))
                        }
                        if all(cleaned_recipe.values()):
                            batch.add_object(properties=cleaned_recipe)

                print(f"\rProgress: {((batch_num + 1) / batches * 100):.1f}% ({end_idx}/{total} recipes)", end='',
                      flush=True)

            print("\nImport completed!")

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _backup_exists(self) -> bool:
        """Check if a backup exists in the specified path."""
        return os.path.exists(self.backup_path) and len(os.listdir(self.backup_path)) > 0

    def _create_and_backup_db(self):
        """Create new database and save backup."""
        try:
            # Create new collection
            self._create_collection_from_schema()
            self._initialize_from_huggingface()

            # Create backup
            print("\nCreating backup...")
            self._create_backup()
            print("Backup created successfully!")

        except Exception as e:
            print(f"Error creating database: {e}")
            raise

    def _create_backup(self):
        """Create a backup of the database."""
        try:
            # Ensure backup directory exists
            os.makedirs(self.backup_path, exist_ok=True)

            # Create backup
            backup_id = f"backup_{int(time.time())}"
            self.client.backup.create(
                backup_id=backup_id,
                backend="filesystem",
                include_collections=[self.collection_name],
                wait_for_completion=True,
                backend_settings={
                    "local_path": self.backup_path
                }
            )

            # Save backup ID for future reference
            with open(os.path.join(self.backup_path, "latest_backup.txt"), "w") as f:
                f.write(backup_id)

        except Exception as e:
            print(f"Error creating backup: {e}")
            raise

    def _restore_from_backup(self):
        """Restore database from backup."""
        try:
            # Get latest backup ID
            with open(os.path.join(self.backup_path, "latest_backup.txt"), "r") as f:
                backup_id = f.read().strip()

            print(f"Restoring from backup: {backup_id}")

            # Restore backup
            self.client.backup.restore(
                backup_id=backup_id,
                backend="filesystem",
                include_collections=[self.collection_name],
                wait_for_completion=True,
                backend_settings={
                    "local_path": self.backup_path
                }
            )

            # Get the restored collection
            self.collection = self.client.collections.get(self.collection_name)

            # Verify restoration
            count = self.collection.aggregate.over_all(total_count=True).total_count
            print(f"Restored {count} recipes successfully!")

        except Exception as e:
            print(f"Error restoring backup: {e}")
            raise

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

    def search_similar_recipes_by_ingredients(self, ingredients: str, limit: int = 3) -> List[Dict]:
        """Search for recipes by matching ingredients."""
        try:
            print(f"Searching for recipes with ingredients similar to: {ingredients}")

            response = self.collection.query.near_text(
                query=ingredients,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    if not obj.properties.get("ingredients"):  # Skip if no ingredients
                        continue

                    recipe = {
                        "title": obj.properties.get("title", "Recipe Title Not Available"),
                        "ingredients": obj.properties["ingredients"],
                        "instructions": obj.properties.get("instructions", "Instructions not available"),
                        "similarity_score": 1 - getattr(obj.metadata, 'distance', 0)
                    }
                    results.append(recipe)
                    print(f"Found recipe: {recipe['title']} (similarity: {recipe['similarity_score']:.2f})")

            if not results:
                print("No matching recipes found")

            # Sort by similarity score
            return sorted(results, key=lambda x: x['similarity_score'], reverse=True)

        except Exception as e:
            print(f"Error in recipe search: {e}")
            import traceback
            traceback.print_exc()
            return []

    def search_by_title(self, title: str, limit: int = 3) -> List[Dict]:
        """Search recipes by title."""
        try:
            # For title-focused search
            response = self.collection.query.near_text(
                query=title,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    if not obj.properties.get("title"):
                        continue

                    recipe = {
                        "title": obj.properties["title"],
                        "ingredients": obj.properties.get("ingredients", "No ingredients available"),
                        "instructions": obj.properties.get("instructions", "No instructions available"),
                        "similarity_score": 1 - getattr(obj.metadata, 'distance', 0)
                    }
                    results.append(recipe)

            return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
        except Exception as e:
            print(f"Error in title search: {e}")
            import traceback
            traceback.print_exc()
            return []

    def search_by_instructions(self, instruction_text: str, limit: int = 3) -> List[Dict]:
        """Search recipes by cooking instructions."""
        try:
            response = self.collection.query.near_text(
                query=instruction_text,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    if not obj.properties.get("instructions"):
                        continue

                    recipe = {
                        "title": obj.properties.get("title", "Untitled Recipe"),
                        "ingredients": obj.properties.get("ingredients", "No ingredients available"),
                        "instructions": obj.properties["instructions"],
                        "similarity_score": 1 - getattr(obj.metadata, 'distance', 0)
                    }
                    results.append(recipe)

            return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
        except Exception as e:
            print(f"Error in instruction search: {e}")
            import traceback
            traceback.print_exc()
            return []

    def advanced_recipe_search(self, query: str, search_fields: List[str] = None, limit: int = 3) -> List[Dict]:
        """
        Search recipes with emphasis on specified fields.
        """
        try:
            if not search_fields:
                search_fields = ["ingredients"]

            response = self.collection.query.near_text(
                query=query,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    recipe = {
                        "title": obj.properties.get("title", "Untitled Recipe"),
                        "matched_fields": {}
                    }

                    # Add only the requested fields
                    for field in search_fields:
                        recipe[field] = obj.properties.get(field, f"No {field} available")
                        if obj.properties.get(field):
                            recipe["matched_fields"][field] = True

                    recipe["similarity_score"] = 1 - getattr(obj.metadata, 'distance', 0)

                    # Only add if we found content in any of the requested fields
                    if any(obj.properties.get(field) for field in search_fields):
                        results.append(recipe)

            return sorted(results, key=lambda x: x['similarity_score'], reverse=True)

        except Exception as e:
            print(f"Error in advanced search: {e}")
            import traceback
            traceback.print_exc()
            return []

def get_similar_recipes(ingredients, db=None):
    """Get recipes that match the given ingredients."""
    if db is None:
        db = RecipeDB()

    fields = ['ingredients','title','instructions']
    recipes = db.advanced_recipe_search(ingredients, fields)
    return recipes


if __name__ == '__main__':
    db = RecipeDB()

    while True:
        print("\nSearch options:")
        print("1. Search by ingredients (default)")
        print("2. Search by title")
        print("3. Search by cooking method/instructions")
        print("4. Advanced search")
        print("5. Quit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == '5':
            break

        query = input("Enter search text: ").strip()

        if choice == '1' or choice == '':
            recipes = db.search_similar_recipes_by_ingredients(query)
        elif choice == '2':
            recipes = db.search_by_title(query)
        elif choice == '3':
            recipes = db.search_by_instructions(query)
        elif choice == '4':
            print("\nSelect fields to search (comma-separated):")
            print("Available fields: title, ingredients, instructions")
            fields = [f.strip() for f in input("Fields: ").split(',')]
            recipes = db.advanced_recipe_search(query, fields)

        # Pretty print results
        print("\nResults:")
        for recipe in recipes:
            print(f"\nTitle: {recipe['title']}")
            print(f"Similarity: {recipe['similarity_score']:.2f}")

            if recipe.get('ingredients'):
                try:
                    # Try to parse the ingredients string into a list
                    ingredients_list = eval(recipe['ingredients'])
                    print("\nIngredients:")
                    for ing in ingredients_list[:10]:
                        print(f"- {ing}")
                    if len(ingredients_list) > 10:
                        print("...")
                except:
                    # Fallback if parsing fails
                    print("\nIngredients:", recipe['ingredients'][:200], "...")

            if recipe.get('instructions'):
                print("\nInstructions:")
                print(f"{recipe['instructions'][:200]}...")
            print("-" * 80)
