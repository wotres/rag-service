from fastapi import APIRouter, HTTPException
from models.document_model import DocumentCreate, DocumentUpdate
from services import document_service
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def router_lifespan(app: FastAPI):
    print("⚙️ Document 스키마 확인 중...")
    document_service.init_schema()
    yield
    print("✅ Document 라우터 종료")

router = APIRouter(lifespan=router_lifespan)


@router.post("", summary="문서 생성")
async def create_document(doc: DocumentCreate):
    return await document_service.create_document(doc)


@router.get("/{doc_id}", summary="문서 조회")
def get_document(doc_id: str):
    doc = document_service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("", summary="문서 목록")
def list_documents(limit: int = 10):
    return document_service.list_documents(limit)

@router.get("/title/{title}", summary="특정 title의 문서(청크) 목록 조회")
def list_documents_by_title(title: str, limit: int = 10):
    """
    동일 title로 저장된 모든 청크(문서 조각)들을 반환.
    """
    docs = document_service.list_documents_by_title(title, limit)
    if not docs:
        raise HTTPException(status_code=404, detail=f"No documents found with title '{title}'")
    return docs

@router.put("/{doc_id}", summary="문서 수정 (id 기반)")
async def update_document(doc_id: str, doc_update: DocumentUpdate):
    if not doc_update.content:
        raise HTTPException(status_code=400, detail="content is required for update")

    try:
        updated = await document_service.update_document_by_id(
            doc_id,
            new_content=doc_update.content,
            new_title=doc_update.title,  # ✅ title 전달
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {e}")


@router.delete("/title/{title}", summary="title 기반 문서 전체 삭제")
def delete_documents_by_title(title: str):
    """
    같은 title을 가진 모든 문서를 삭제합니다.
    """
    try:
        result = document_service.delete_documents_by_title(title)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")




@router.delete("/{doc_id}", summary="문서 삭제")
def delete_document(doc_id: str):
    return document_service.delete_document(doc_id)
