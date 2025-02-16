import weaviate
from weaviate.classes import config as wvcc
from weaviate.classes.query import MetadataQuery
from weaviate.collections.classes.filters import Filter
import pandas as pd
import yaml
from typing import Dict, List, Any, Optional
import atexit

class IngredientsDB:
    def __init__(self, collection_name: str = "Ingredients", schema_path: str = "schema.yaml"):
        """Initialize the ingredients database with error handling and connection management."""
        try:
            self.client = weaviate.connect_to_local()
            self.collection_name = collection_name
            self.schema_path = schema_path
            atexit.register(self.close)
            
            self._ensure_collection()
            
        except Exception as e:
            print(f"Failed to initialize IngredientsDB: {e}")
            raise

    def _ensure_collection(self) -> None:
        """Ensure collection exists and is properly initialized."""
        try:
            try:
                # Check if collection exists
                collections = self.client.collections.list_all()
                exists = any(c.name == self.collection_name.lower() for c in collections)
                
                if exists:
                    self.collection = self.client.collections.get(self.collection_name.lower())
                    # Use fetch_objects to check if collection has data
                    objects = self.collection.query.fetch_objects(limit=1)
                    if hasattr(objects, 'objects') and len(objects.objects) > 0:
                        print(f"Connected to existing collection: {self.collection_name}")
                        return
                    else:
                        print("Collection exists but is empty")
                        self.client.collections.delete(self.collection_name.lower())
                
            except weaviate.exceptions.UnexpectedStatusCodeError:
                print("Creating new collection...")
            
            self._create_collection()
            self._initialize_data()
            
        except Exception as e:
            print(f"Error ensuring collection: {e}")
            raise

    def _create_collection(self) -> None:
        """Create collection with schema."""
        try:
            with open(self.schema_path, 'r') as file:
                schema = yaml.safe_load(file)

            properties = [
                wvcc.Property(name=prop['name'], data_type=wvcc.DataType.TEXT)
                for prop in schema['properties']
            ]

            self.collection = self.client.collections.create(
                name=self.collection_name,
                vectorizer_config=wvcc.Configure.Vectorizer.text2vec_transformers(),
                properties=properties
            )
            print(f"Created collection: {self.collection_name}")
            
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise

    def _initialize_data(self) -> None:
        """Initialize database with ingredient data."""
        try:
            print("Loading data from HuggingFace...")
            df = pd.read_parquet(
                "hf://datasets/foodvisor-nyu/labeled-food-ingredients/data/train-00000-of-00001.parquet"
            )
            
            ingredients_list = df.to_dict('records')
            self._batch_import(ingredients_list)
            
        except Exception as e:
            print(f"Error initializing data: {e}")
            raise

    def _batch_import(self, ingredients: List[Dict[str, Any]]) -> None:
        """Import ingredients in batches with progress tracking."""
        try:
            total = len(ingredients)
            batch_size = 100
            batches = (total + batch_size - 1) // batch_size

            print(f"\nImporting {total} ingredients in {batches} batches:")

            for i in range(batches):
                start = i * batch_size
                end = min(start + batch_size, total)
                
                with self.collection.batch.dynamic() as batch:
                    for ingredient in ingredients[start:end]:
                        cleaned = {
                            k: str(v) if v is not None else ''
                            for k, v in ingredient.items()
                            if k in ['ingredient', 'class', 'reason', 'int_label', 'prompt']
                        }
                        batch.add_object(properties=cleaned)
                
                print(f"\rProgress: {((i + 1) / batches * 100):.1f}% ({end}/{total})", end='')
            print("\nImport completed!")
            
        except Exception as e:
            print(f"Error in batch import: {e}")
            raise

    def search_similar_ingredients(self, ingredient: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar ingredients with error handling."""
        try:
            response = self.collection.query.near_text(
                query=ingredient,
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

            return sorted(results, key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            print(f"Error searching ingredients: {e}")
            return []

    def close(self) -> None:
        """Safely close database connection."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

def get_similar_ingredients(ingredient: str, db: Optional[IngredientsDB] = None) -> List[str]:
    """Get similar ingredients, optionally reusing an existing database connection."""
    try:
        if db is None:
            db = IngredientsDB()
        
        similar = db.search_similar_ingredients(ingredient)
        return [item['ingredient'] for item in similar]
        
    except Exception as e:
        print(f"Error getting similar ingredients: {e}")
        return []

if __name__ == '__main__':
    db = IngredientsDB()
    while True:
        query = input('Ingredient (or "quit" to exit): ').strip()
        if query.lower() == 'quit':
            break
        results = get_similar_ingredients(query, db)
        print("\nSimilar ingredients:")
        for i, ingredient in enumerate(results, 1):
            print(f"{i}. {ingredient}")
