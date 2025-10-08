import httpx
from config.settings import settings


async def get_embedding_from_model_server(query: str):
    """
    외부 모델 서버에 query를 전송해 embedding 벡터를 가져옴 (비동기)
    """
    embedding_url = f"{settings.MODEL_SERVER_URL}/v1/embeddings"

    async with httpx.AsyncClient(timeout=10.0) as client:

        response = await client.post(
            embedding_url,
            json={
                "model": "mock-embedding",  # mock 서버는 model 필드도 요구함
                "input": query              # mock 서버는 'input' 필드 사용
            },
        )
        response.raise_for_status()
        data = response.json()
        # ✅ mock embedding 서버의 응답 구조에 맞춰 추출
        return data["data"][0]["embedding"]
