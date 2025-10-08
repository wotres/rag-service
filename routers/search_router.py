from fastapi import APIRouter, HTTPException
from models.search_models import QueryRequest, QueryResponse
from services.embedding_service import get_embedding_from_model_server
from services.weaviate_service import search_similar_docs

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def search_by_query(request: QueryRequest):
    """
    1️⃣ 모델 서버에서 embedding 벡터 생성 (비동기)
    2️⃣ Weaviate에서 유사도 top3 문서 조회
    """
    try:
        query_vector = await get_embedding_from_model_server(request.query)
        results = search_similar_docs(query_vector, top_k=3)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
