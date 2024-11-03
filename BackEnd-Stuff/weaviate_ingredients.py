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
                grpc_port=grpc_port
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
        Find similar ingredients based on text description.

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
                ["name", "category", "taste_profile", "cuisine_types", "description"]
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

    def find_ingredient_substitutes(self,
                                    ingredient_name: str,
                                    limit: int = 5,
                                    same_category: bool = True) -> List[Dict[str, Any]]:
        """
        Find possible substitutes for an ingredient.

        Args:
            ingredient_name: Name of the ingredient to find substitutes for
            limit: Maximum number of substitutes to return
            same_category: If True, only return substitutes from the same category

        Returns:
            List of possible substitute ingredients
        """
        try:
            # First get the original ingredient's properties
            original = self.client.query.get(
                "Ingredient",
                ["name", "category", "taste_profile"]
            ).with_where({
                "path": ["name"],
                "operator": "Equal",
                "valueString": ingredient_name
            }).do()

            orig_data = original.get("data", {}).get("Get", {}).get("Ingredient", [])
            if not orig_data:
                raise IngredientDatabaseError(f"Ingredient '{ingredient_name}' not found")

            orig_ingredient = orig_data[0]

            # Build query for substitutes
            query = self.client.query.get(
                "Ingredient",
                ["name", "category", "taste_profile", "description"]
            ).with_near_text({
                "concepts": [orig_ingredient["taste_profile"]]
            })

            if same_category:
                query = query.with_where({
                    "path": ["category"],
                    "operator": "Equal",
                    "valueString": orig_ingredient["category"]
                })

            results = query.with_additional(["certainty"]).with_limit(limit).do()

            # Filter out the original ingredient
            substitutes = [
                result for result in results.get("data", {}).get("Get", {}).get("Ingredient", [])
                if result["name"] != ingredient_name
            ]

            return substitutes
        except WeaviateBaseError as e:
            logger.error(f"Failed to find substitutes for {ingredient_name}: {e}")
            raise IngredientDatabaseError(f"Substitute search failed: {e}") from e

    def close(self) -> None:
        """Close the database connection."""
        try:
            self.client.close()
            logger.info("Database connection closed successfully")
        except WeaviateBaseError as e:
            logger.error(f"Error closing database connection: {e}")
            raise IngredientDatabaseError("Failed to close database connection") from e


# Initialize the database
db = IngredientDatabase(schema_path="schema.yaml")

# Add some ingredients
tomato = {
    "name": "Tomato",
    "category": "vegetable",
    "taste_profile": "sweet, acidic, umami",
    "cuisine_types": ["Italian", "Mediterranean", "Mexican"],
    "description": "Red, juicy fruit commonly used as a vegetable. Rich in umami flavor."
}

db.add_ingredient(tomato)

# Find similar ingredients
similar = db.find_similar_ingredients(
    "red acidic fruit vegetable",
    limit=3
)
print("Similar ingredients:", similar)

# Find substitutes for tomato
substitutes = db.find_ingredient_substitutes(
    "Tomato",
    limit=3,
    same_category=True
)
print("Possible substitutes:", substitutes)