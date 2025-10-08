import weaviate
from config.settings import settings
from weaviate.classes.query import MetadataQuery

client = weaviate.connect_to_local(
    host=settings.WEAVIATE_HOST,
    port=settings.WEAVIATE_HTTP_PORT,
    grpc_port=settings.WEAVIATE_GRPC_PORT,
)


def search_similar_docs(query_vector: list, top_k: int = 3):
    """
    query_vector를 이용해 Weaviate에서 유사한 문서 검색
    """
    collection = client.collections.get("Document")
    response = collection.query.near_vector(
        near_vector=query_vector,
        limit=top_k,
        return_metadata=MetadataQuery(distance=True)
    )

    docs = [
        {
            "title": obj.properties.get("title"),
            "content": obj.properties.get("content"),
            "distance": obj.metadata.distance
        }
        for obj in response.objects
    ]
    return docs
