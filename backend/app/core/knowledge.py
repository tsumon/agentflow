"""Knowledge Base — simple vector-like document store for RAG."""
import json
import os
from typing import Optional


class Document:
    def __init__(self, id: str, title: str, content: str, metadata: dict = None):
        self.id = id
        self.title = title
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
        }


class KnowledgeBase:
    """Simple in-memory knowledge base with keyword search.

    For production, replace with a vector database (ChromaDB, Pinecone, etc.)
    and proper embeddings.
    """

    def __init__(self, storage_path: str = "./knowledge_base.json"):
        self.storage_path = storage_path
        self.documents: dict[str, Document] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for doc_data in data:
                    doc = Document(**doc_data)
                    self.documents[doc.id] = doc
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    def _save(self):
        data = [doc.to_dict() for doc in self.documents.values()]
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, doc_id: str, title: str, content: str, metadata: dict = None) -> Document:
        doc = Document(id=doc_id, title=title, content=content, metadata=metadata)
        self.documents[doc_id] = doc
        self._save()
        return doc

    def remove(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save()
            return True
        return False

    def get(self, doc_id: str) -> Optional[Document]:
        return self.documents.get(doc_id)

    def search(self, query: str, top_k: int = 5) -> list[Document]:
        """Keyword-based search with TF-like scoring."""
        query_terms = query.lower().split()
        scored = []

        for doc in self.documents.values():
            text = f"{doc.title} {doc.content}".lower()
            score = sum(text.count(term) for term in query_terms)
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    def list_all(self) -> list[Document]:
        return list(self.documents.values())

    def get_context_for_prompt(self, query: str, top_k: int = 3) -> str:
        """Format search results as prompt context."""
        docs = self.search(query, top_k)
        if not docs:
            return ""

        lines = ["\n## Relevant Knowledge Base Documents:\n"]
        for i, doc in enumerate(docs, 1):
            lines.append(f"### [{i}] {doc.title}")
            lines.append(doc.content[:1000])
            if len(doc.content) > 1000:
                lines.append("...(truncated)")
            lines.append("")
        return "\n".join(lines)


# Singleton
knowledge_base = KnowledgeBase()
