"""REST API — Task management endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_session, TaskRecord, MessageRecord

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    description: str = ""


@router.get("/")
async def list_tasks(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(TaskRecord).order_by(TaskRecord.created_at.desc())
    )
    tasks = result.scalars().all()
    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tasks
        ]
    }


@router.post("/")
async def create_task(req: TaskCreate, session: AsyncSession = Depends(get_session)):
    task = TaskRecord(title=req.title, description=req.description, status="pending")
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return {"id": task.id, "title": task.title, "status": task.status}


@router.get("/{task_id}")
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TaskRecord).where(TaskRecord.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "plan": task.plan,
        "result": task.result,
        "error": task.error,
        "execution_log": task.execution_log,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }


@router.delete("/{task_id}")
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TaskRecord).where(TaskRecord.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return {"deleted": True}
