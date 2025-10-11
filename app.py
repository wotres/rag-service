from fastapi import FastAPI
from routers.search_router import router as search_router
from routers.document_router import router as document_router


app = FastAPI(title="RAG Service")

app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(document_router, prefix="/documents", tags=["Documents"])
