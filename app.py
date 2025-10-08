from fastapi import FastAPI
from routers.search_router import router as search_router

app = FastAPI(title="RAG Service")

app.include_router(search_router, prefix="/search", tags=["Search"])
