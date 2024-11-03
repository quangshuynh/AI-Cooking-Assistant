import weaviate
from venv import logger
from weaviate.exceptions import WeaviateBaseError

class DatabaseManager:
    def __init__(self, http_host: str = "Oliver", http_port: int = 8080, grpc_port: int = 50051,
                 grpc_secure: bool = False, http_secure: bool = False):
        try:
            self.client = weaviate.connect_to_custom(
                http_host=http_host,
                http_secure=http_secure,
                grpc_host=http_host,
                grpc_port=grpc_port,
                grpc_secure=grpc_secure,
                http_port=http_port
            )
            logger.info("Weaviate client initialized successfully.")
        except WeaviateBaseError as e:
            logger.error(f"Failed to initialize Weaviate client: {e}")
            raise MemoryError("Weaviate client initialization failed.") from e
