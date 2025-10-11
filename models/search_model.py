from pydantic import BaseModel
from typing import List, Any


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    results: List[Any]
