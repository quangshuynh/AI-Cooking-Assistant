import logging
import yaml
import weaviate
from weaviate.exceptions import WeaviateBaseError
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class IngredientDatabaseError(Exception):
    """Custom exception for ingredient database operations."""
    pass


class IngredientDatabase:
    def __init__(self, http_host: str = "localhost", http_port: int = 8080,
                 grpc_port: int = 50051, schema_path: str = "schema.yaml"):
        """
        Initialize the ingredient database.

        Args:
            http_host: Weaviate host address
            http_port: HTTP port for Weaviate
            grpc_port: gRPC port for Weaviate
            schema_path: Path to the schema YAML file
        """
        try:
            self.client = weaviate.connect_to_custom(
                http_host=http_host,
                http_port=http_port,
                grpc_host=http_host,
                grpc_port=grpc_port,
                http_secure=False,  # Set to True if using HTTPS
                grpc_secure=False   # Set to True if using gRPCs
            )
            self.schema = self._load_schema(schema_path)
            self._initialize_schema()
            logger.info("Ingredient database initialized successfully")
        except WeaviateBaseError as e:
            logger.error(f"Failed to initialize ingredient database: {e}")
            raise IngredientDatabaseError("Database initialization failed") from e

    def _load_schema(self, schema_path: str) -> dict:
        """Load schema from YAML file."""
        try:
            with open(schema_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load schema from {schema_path}: {e}")
            raise IngredientDatabaseError(f"Schema loading failed: {e}") from e

    def _initialize_schema(self) -> None:
        """Initialize the Weaviate schema."""
        try:
            for class_obj in self.schema['classes']:
                if not self.client.schema.exists(class_obj['class']):
                    self.client.schema.create_class(class_obj)
                    logger.info(f"Created class: {class_obj['class']}")
        except WeaviateBaseError as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise IngredientDatabaseError(f"Schema initialization failed: {e}") from e

    def add_ingredient(self, ingredient: Dict[str, Any]) -> str:
        """
        Add a single ingredient to the database.

        Args:
            ingredient: Dictionary containing ingredient properties

        Returns:
            UUID of the created object
        """
        try:
            return self.client.data_object.create(
                data_object=ingredient,
                class_name="Ingredient"
            )
        except WeaviateBaseError as e:
            logger.error(f"Failed to add ingredient {ingredient.get('name')}: {e}")
            raise IngredientDatabaseError(f"Ingredient addition failed: {e}") from e

    def find_similar_ingredients(self,
                               query_text: str,
                               limit: int = 5,
                               min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find similar ingredients based on text description and safety classification.

        Args:
            query_text: Text to search similar ingredients for
            limit: Maximum number of results to return
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of similar ingredients with their properties
        """
        try:
            vector = self.client.query.get(
                "Ingredient",
                ["name", "safety_class", "reason", "int_label"]
            ).with_near_text({
                "concepts": [query_text]
            }).with_additional(["certainty"]).with_limit(limit).do()

            results = vector.get("data", {}).get("Get", {}).get("Ingredient", [])

            # Filter by minimum similarity
            filtered_results = [
                result for result in results
                if result.get("_additional", {}).get("certainty", 0) >= min_similarity
            ]

            return filtered_results
        except WeaviateBaseError as e:
            logger.error(f"Failed to search similar ingredients: {e}")
            raise IngredientDatabaseError(f"Similarity search failed: {e}") from e

    def find_ingredients_by_safety(self,
                                 safety_class: str,
                                 limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find ingredients by their safety classification.

        Args:
            safety_class: Safety classification to search for (e.g., 'controversial', 'not harmful')
            limit: Maximum number of results to return

        Returns:
            List of ingredients with the specified safety classification
        """
        try:
            results = self.client.query.get(
                "Ingredient",
                ["name", "safety_class", "reason", "int_label"]
            ).with_where({
                "path": ["safety_class"],
                "operator": "Equal",
                "valueString": safety_class
            }).with_limit(limit).do()

            return results.get("data", {}).get("Get", {}).get("Ingredient", [])
        except WeaviateBaseError as e:
            logger.error(f"Failed to find ingredients by safety class: {e}")
            raise IngredientDatabaseError(f"Safety class search failed: {e}") from e


# Example usage:
if __name__ == "__main__":
    # Initialize the database
    db = IngredientDatabase(schema_path="schema.yaml")

    # Add an ingredient
    acacia_gum = {
        "name": "acacia gum",
        "safety_class": "not harmful",
        "reason": "Acacia gum, also known as gum arabic, is a natural dietary fiber used as a food additive.",
        "int_label": 2
    }

    db.add_ingredient(acacia_gum)

    # Find similar ingredients
    similar = db.find_similar_ingredients(
        "natural gum ingredient",
        limit=3
    )
    print("Similar ingredients:", similar)

    # Find ingredients by safety class
    safe_ingredients = db.find_ingredients_by_safety(
        "not harmful",
        limit=3
    )
    print("Safe ingredients:", safe_ingredients)