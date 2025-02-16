import atexit
import yaml
import pandas as pd
import weaviate
from weaviate.classes import config as wvcc
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.filters import Filter
from typing import Dict, List, Any
from .Vector_Database_Ingredients import IngredientsDB, get_similar_ingredients

class IngredientDBEfficient(IngredientsDB):
    def __init__(self, collection_name="Ingredients", schema_path="schema.yaml"):
        super().__init__(collection_name, schema_path)
        atexit.register(self.close)

        try:
            # Try to get the existing collection first
            self.collection = self.client.collections.get(self.collection_name)
            print(f"Connected to existing collection: {self.collection_name}")
        except weaviate.exceptions.UnexpectedStatusCodeError:
            # If collection doesn't exist, create it
            print(f"Creating new collection: {self.collection_name}")
            self._create_collection_from_schema()
            self._initialize_from_huggingface()

    def _create_collection_from_schema(self):
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
        except weaviate.exceptions.UnexpectedStatusCodeError as e:
            # If collection was created in the meantime, try to get it
            if "already exists" in str(e):
                self.collection = self.client.collections.get(self.collection_name)
            else:
                raise

    def _initialize_from_huggingface(self):
        try:
            print("Loading data from HuggingFace...")
            df = pd.read_parquet(
                "hf://datasets/foodvisor-nyu/labeled-food-ingredients/data/train-00000-of-00001.parquet")
            print(f"Loaded {len(df)} records from HuggingFace")

            ingredients_list = df.to_dict('records')
            success = self.batch_import_ingredients(ingredients_list)
            if success:
                print(f"Successfully imported {len(ingredients_list)} ingredients")
            else:
                print("Failed to import ingredients")
        except Exception as e:
            print(f"Error loading data from HuggingFace: {e}")
            raise

    def batch_import_ingredients(self, ingredients_list: List[Dict[str, Any]]) -> bool:
        try:
            with self.collection.batch.dynamic() as batch:
                for ingredient in ingredients_list:
                    cleaned_ingredient = {
                        k: '' if pd.isna(v) else str(v)
                        for k, v in ingredient.items()
                        if k in ['ingredient', 'class', 'reason', 'int_label', 'prompt']
                    }
                    batch.add_object(properties=cleaned_ingredient)
            return True
        except Exception as e:
            print(f"Error in batch import: {e}")
            return False

    def get_statistics(self) -> Dict:
        try:
            # Get total count
            total_count_response = self.collection.aggregate.over_all(
                total_count=True
            )
            total_count = total_count_response.total_count

            # Get class distribution using aggregate
            class_counts = self.collection.aggregate.over_all().group_by(
                property_name="class"
            ).objects

            class_distribution = {}
            for group in class_counts:
                if hasattr(group, 'properties'):
                    class_name = group.properties.get('class', 'unknown')
                    count = group.count
                    class_distribution[class_name] = count

            return {
                "total_ingredients": total_count,
                "class_distribution": class_distribution
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {"total_ingredients": 0, "class_distribution": {}}

    def search_similar_ingredients(self, query_text: str, limit: int = 5) -> List[Dict]:
        try:
            response = self.collection.query.near_text(
                query=query_text,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    results.append({
                        "properties": obj.properties,
                        "distance": getattr(obj.metadata, 'distance', 0)
                    })
            return results
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []

    def search_by_class(self, class_type: str, limit: int = 5) -> List[Dict]:
        try:
            # Create filter using Filter class
            class_filter = Filter.by_property("class") == class_type

            response = self.collection.query.fetch_objects(
                limit=limit,
                filters=class_filter
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    results.append({
                        "ingredient": obj.properties.get("ingredient", ""),
                        "class": obj.properties.get("class", ""),
                        "reason": obj.properties.get("reason", "")
                    })
            return results
        except Exception as e:
            print(f"Error in class search: {e}")
            return []

    def close(self):
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

    def search_similar_ingredients_by_name(self, ingredient_name: str, limit: int = 5) -> List[Dict]:
        """
        Search for ingredients with similar names to the provided ingredient name.

        Args:
            ingredient_name: The name of the ingredient to find similar matches for
            limit: Maximum number of results to return

        Returns:
            List of similar ingredients with their similarity scores
        """
        try:
            # Use near_text instead of hybrid for better compatibility
            response = self.collection.query.near_text(
                query=ingredient_name,
                limit=limit,
                return_metadata=MetadataQuery(distance=True)
            )

            results = []
            if hasattr(response, 'objects'):
                for obj in response.objects:
                    results.append({
                        "ingredient": obj.properties.get("ingredient", ""),
                        "class": obj.properties.get("class", ""),
                        "reason": obj.properties.get("reason", ""),
                        "similarity_score": 1 - getattr(obj.metadata, 'distance', 0)
                    })

            # Sort results by similarity score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results
        except Exception as e:
            print(f"Error in name similarity search: {e}")
            return []

    def get_ingredient_details(self, ingredient_name: str) -> Dict:
        """
        Get full details for a specific ingredient by exact name match.
        """
        try:
            filter_by_name = Filter.by_property("ingredient") == ingredient_name
            response = self.collection.query.fetch_objects(
                limit=1,
                filters=filter_by_name
            )

            if hasattr(response, 'objects') and len(response.objects) > 0:
                obj = response.objects[0]
                return {
                    "ingredient": obj.properties.get("ingredient", ""),
                    "class": obj.properties.get("class", ""),
                    "reason": obj.properties.get("reason", ""),
                    "int_label": obj.properties.get("int_label", ""),
                    "prompt": obj.properties.get("prompt", "")
                }
            return {}
        except Exception as e:
            print(f"Error getting ingredient details: {e}")
            return {}


def get_similar_ingredients(ingredient, db=None):
    # Initialize the database only if not provided
    if db is None:
        db = IngredientDBEfficient()

    similar_ingredients = db.search_similar_ingredients(ingredient, limit=5)
    return [ingre['properties']['ingredient'] for ingre in similar_ingredients] if similar_ingredients else []


if __name__ == '__main__':
    # Initialize once
    db = IngredientDBEfficient()

    # Reuse the same connection for multiple queries
    while True:
        user_input = input('Ingredient (or "quit" to exit): ')
        if user_input.lower() == 'quit':
            break
        results = get_similar_ingredients(user_input, db=db)
        print("\nSimilar ingredients:")
        for i, ingredient in enumerate(results, 1):
            print(f"{i}. {ingredient}")
