import weaviate
from config.settings import settings
from weaviate.classes.query import Filter, MetadataQuery

client = weaviate.connect_to_local(
    host=settings.WEAVIATE_HOST,
    port=settings.WEAVIATE_HTTP_PORT,
    grpc_port=settings.WEAVIATE_GRPC_PORT,
)



def search_similar_docs(title: str, query_vector: list, top_k: int = 3):
    """
    title이 정확히 일치하는 문서 범위 안에서만 near_vector로 유사 검색.
    - title 일치하는 문서가 하나도 없으면 [] 반환
    """
    collection = client.collections.get("Document")

    title_filter = Filter.by_property("title").equal(title)

    response = collection.query.near_vector(
        near_vector=query_vector,
        limit=top_k,
        filters=title_filter,                             # <-- title 일치로 사전 필터
        return_properties=["title", "content"],           # 필요한 프로퍼티만
        return_metadata=MetadataQuery(distance=True),
    )

    if not response.objects:  # title 일치하는 문서가 없는 경우
        return []

    docs = [
        {
            "title": obj.properties.get("title"),
            "content": obj.properties.get("content"),
            "distance": obj.metadata.distance,
        }
        for obj in response.objects
    ]
    return docs

