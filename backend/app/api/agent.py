"""REST API — Agent endpoints."""
import json
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_session, AgentRecord
from app.agents.orchestrator import orchestrator
from app.agents.planner import PlannerAgent
from app.agents.executor import ExecutorAgent
from app.agents.reviewer import ReviewerAgent

router = APIRouter(prefix="/api/agents", tags=["agents"])


# --- Schemas ---

class TaskRequest(BaseModel):
    task: str = Field(..., description="Task description")
    kb_query: str = Field("", description="Optional knowledge base query")
    mode: str = Field("pipeline", description="pipeline | direct")


class ChatRequest(BaseModel):
    message: str = Field(..., description="Chat message")
    stream: bool = Field(False)


# --- Endpoints ---

@router.get("/")
async def list_agents():
    """List available agents."""
    return {
        "agents": [
            {
                "name": "Planner",
                "role": "planner",
                "description": "Strategic task planning and decomposition",
                "tools": ["json_parse"],
            },
            {
                "name": "Executor",
                "role": "executor",
                "description": "Task execution with full tool access",
                "tools": ["calculator", "search", "read_file", "write_file", "web_fetch", "json_parse"],
            },
            {
                "name": "Reviewer",
                "role": "reviewer",
                "description": "Quality review and output validation",
                "tools": ["json_parse"],
            },
        ]
    }


@router.post("/run")
async def run_task(req: TaskRequest):
    """Run a task through the agent pipeline."""
    if not req.task.strip():
        raise HTTPException(status_code=400, detail="Task description is required")

    result = await orchestrator.process(
        task=req.task,
        kb_query=req.kb_query,
    )
    return result


@router.post("/chat")
async def chat(req: ChatRequest):
    """Direct chat with the executor agent."""
    if req.stream:
        async def event_stream():
            async for chunk in orchestrator.direct_chat_stream(req.message):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
        )

    result = await orchestrator.direct_chat(req.message)
    return {"response": result}


@router.get("/tools")
async def list_tools():
    """List all available tools."""
    from app.core.tools import TOOL_REGISTRY
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in TOOL_REGISTRY.values()
        ]
    }
