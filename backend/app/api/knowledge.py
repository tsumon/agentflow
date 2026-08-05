"""REST API — Knowledge Base endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.knowledge import knowledge_base

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class DocCreate(BaseModel):
    doc_id: str = Field(..., alias="docId")
    title: str
    content: str
    metadata: dict = Field(default_factory=dict, alias="metadata")


class DocSearch(BaseModel):
    query: str
    top_k: int = Field(5, alias="topK")


@router.get("/")
async def list_docs():
    docs = knowledge_base.list_all()
    return {
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "content_preview": d.content[:200],
                "metadata": d.metadata,
            }
            for d in docs
        ]
    }


@router.post("/")
async def add_doc(req: DocCreate):
    doc = knowledge_base.add(
        doc_id=req.doc_id,
        title=req.title,
        content=req.content,
        metadata=req.metadata,
    )
    return {"id": doc.id, "title": doc.title, "status": "added"}


@router.delete("/{doc_id}")
async def delete_doc(doc_id: str):
    if knowledge_base.remove(doc_id):
        return {"deleted": True}
    raise HTTPException(status_code=404, detail="Document not found")


@router.post("/search")
async def search_docs(req: DocSearch):
    docs = knowledge_base.search(req.query, req.top_k)
    return {
        "query": req.query,
        "results": [
            {
                "id": d.id,
                "title": d.title,
                "content": d.content,
                "metadata": d.metadata,
            }
            for d in docs
        ]
    }
