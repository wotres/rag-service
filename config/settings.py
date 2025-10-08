import os


class Settings:
    WEAVIATE_HOST: str = os.getenv("WEAVIATE_HOST", "localhost")
    WEAVIATE_HTTP_PORT: int = int(os.getenv("WEAVIATE_HTTP_PORT", 8080))
    WEAVIATE_GRPC_PORT: int = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))
    MODEL_SERVER_URL: str = os.getenv("MODEL_SERVER_URL", "http://localhost:8888/v1/embeddings")

    class Config:
        env_file = ".env"


settings = Settings()
