from pydantic import BaseModel
from typing import List, Any


class QueryRequest(BaseModel):
    title: str
    query: str


class QueryResponse(BaseModel):
    results: List[Any]
