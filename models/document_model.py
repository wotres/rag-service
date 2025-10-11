from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentUpdate(BaseModel):
    title: str
    content: str
