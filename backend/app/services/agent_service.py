"""Agent Service — business logic layer."""
import json
import logging
from app.agents.orchestrator import orchestrator
from app.core.knowledge import knowledge_base

logger = logging.getLogger(__name__)


class AgentService:
    """High-level service for agent operations."""

    @staticmethod
    async def execute_task(task: str, kb_query: str = "") -> dict:
        """Execute a task through the agent pipeline."""
        return await orchestrator.process(task=task, kb_query=kb_query)

    @staticmethod
    async def chat(message: str) -> str:
        """Direct chat with agent."""
        return await orchestrator.direct_chat(message)

    @staticmethod
    def search_knowledge(query: str, top_k: int = 5) -> list:
        """Search the knowledge base."""
        docs = knowledge_base.search(query, top_k)
        return [d.to_dict() for d in docs]

    @staticmethod
    def add_knowledge(doc_id: str, title: str, content: str, metadata: dict = None) -> dict:
        """Add a document to the knowledge base."""
        doc = knowledge_base.add(doc_id, title, content, metadata)
        return doc.to_dict()
