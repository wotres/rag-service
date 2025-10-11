import weaviate
import weaviate.classes as wvc
import weaviate.classes.config as wc
from config.settings import settings
from models.document_model import DocumentCreate, DocumentUpdate
from typing import List, Dict, Any, Optional
from services.embedding_service import get_embedding_from_model_server

client = weaviate.connect_to_local(
    host=settings.WEAVIATE_HOST,
    port=settings.WEAVIATE_HTTP_PORT,
    grpc_port=settings.WEAVIATE_GRPC_PORT,
)

COLLECTION_NAME = "Document"


def init_schema():
    try:
        if client.collections.exists(COLLECTION_NAME):
            print(f"✅ '{COLLECTION_NAME}' 스키마 이미 존재 — 기존 스키마를 그대로 사용합니다.")
            return

        client.collections.create(
            name=COLLECTION_NAME,
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),  # 벡터라이저 사용 안 함
            properties=[
                wc.Property(name="title", data_type=wc.DataType.TEXT),
                wc.Property(name="content", data_type=wc.DataType.TEXT),
            ],
        )
        print(f"✅ '{COLLECTION_NAME}' 스키마 생성 완료.")
    except Exception as e:
        print(f"⚠️ 스키마 초기화 중 오류 발생: {e}")


def chunk_by_chars(text: str, chunk_size: Optional[int] = None) -> List[str]:
    """
    설정에 정의된 CHUNK_SIZE(기본 100)로 고정 길이 청크 분할.
    겹침(overlap) 없이 단순 고정 길이로 자른다.
    """
    if text is None:
        text = ""
    text = text.strip()
    if not text:
        return []

    size = chunk_size or getattr(settings, "CHUNK_SIZE", 100)
    chunks = [text[i:i+size] for i in range(0, len(text), size)]
    return chunks


async def create_document(doc: DocumentCreate) -> Dict[str, Any]:
    collection = client.collections.get(COLLECTION_NAME)
    chunks = chunk_by_chars(doc.content, chunk_size=getattr(settings, "CHUNK_SIZE", 100))
    created_ids = []
    for chunk_text in chunks:
        vec = await get_embedding_from_model_server(chunk_text)  # ✅ await 필요
        object_id = collection.data.insert(
            properties={"title": doc.title, "content": chunk_text},
            vector=vec,
        )
        created_ids.append(object_id)
    return {"title": doc.title, "chunks": len(chunks), "ids": created_ids}



def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    coll = client.collections.get(COLLECTION_NAME)
    o = coll.query.fetch_object_by_id(doc_id)
    if not o:
        return None
    return {
        "id": o.uuid,
        "title": o.properties.get("title"),
        "content": o.properties.get("content"),
    }

def list_documents(limit: int = 10) -> List[Dict[str, Any]]:
    """
    저장된 모든 문서(청크 단위) 목록을 반환.
    - title, content, id 포함
    - 최신순 정렬은 Weaviate v4 기본 제공 안 함 (필요시 created_at 속성 추가)
    """
    print('hi')
    coll = client.collections.get(COLLECTION_NAME)
    res = coll.query.fetch_objects(
        limit=limit,
        return_properties=["title", "content"],
    )

    return [
        {
            "id": o.uuid,
            "title": o.properties.get("title"),
            "content": o.properties.get("content"),
        }
        for o in res.objects
    ]



def list_documents_by_title(title: str, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    동일 title로 저장된 청크들을 모두 가져온다.
    반환은 청크 단위(각 오브젝트 1개)로 구성.
    """

    coll = client.collections.get(COLLECTION_NAME)
    res = coll.query.fetch_objects(
        limit=limit,
        filters=wvc.query.Filter.by_property("title").equal(title),
        return_properties=["title", "content"],
    )
    # 주의: v4 반환 객체에서 properties 접근은 o.properties
    return [
        {
            "id": o.uuid,
            "title": o.properties.get("title"),
            "content": o.properties.get("content"),  # 청크 텍스트
        }
        for o in res.objects
    ]

async def update_document_by_id(doc_id: str, new_content: str, new_title: Optional[str] = None) -> Dict[str, Any]:
    """
    특정 doc_id의 문서를 수정한다.
    - title도 수정 가능
    - content는 CHUNK_SIZE 기준으로 1개 초과면 오류 발생
    """
    coll = client.collections.get(COLLECTION_NAME)

    # 기존 문서 조회
    existing = coll.query.fetch_object_by_id(doc_id)
    if not existing:
        raise ValueError(f"Document with id '{doc_id}' not found")

    title = new_title or existing.properties.get("title")

    # 청크 검증
    chunks = chunk_by_chars(new_content, chunk_size=getattr(settings, "CHUNK_SIZE", 100))
    if len(chunks) > 1:
        raise ValueError(f"Content too long: exceeds {getattr(settings, 'CHUNK_SIZE', 100)} characters limit")

    # 벡터 재계산
    vec = await get_embedding_from_model_server(new_content)

    # 내용 + title 덮어쓰기
    coll.data.update(
        doc_id,
        properties={"title": title, "content": new_content},
        vector=vec,
    )

    return {
        "id": doc_id,
        "title": title,
        "updated": True,
        "chunk_size": len(new_content),
    }

def delete_documents_by_title(title: str) -> Dict[str, Any]:
    """
    같은 title을 가진 모든 문서(청크)를 삭제한다.
    """
    coll = client.collections.get(COLLECTION_NAME)

    # title에 해당하는 모든 객체 조회
    res = coll.query.fetch_objects(
        filters=wvc.query.Filter.by_property("title").equal(title),
        return_properties=["title", "content"]
    )

    if not res.objects:
        raise ValueError(f"No documents found with title '{title}'")

    deleted_ids = []
    for o in res.objects:
        coll.data.delete_by_id(o.uuid)
        deleted_ids.append(o.uuid)

    return {
        "title": title,
        "deleted_count": len(deleted_ids),
        "deleted_ids": deleted_ids
    }




def delete_document(doc_id: str) -> Dict[str, str]:
    coll = client.collections.get(COLLECTION_NAME)
    coll.data.delete_by_id(doc_id)
    return {"deleted_id": doc_id}
