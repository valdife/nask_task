from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_task(self, task_id: str) -> Optional[Task]:
        result: Result[Task, Any] = await self.db.execute(
            select(Task).filter(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        task_result: Optional[dict] = None,
        error: Optional[str] = None,
    ):
        result: Result[Task, Any] = await self.db.execute(
            select(Task).filter(Task.id == task_id)
        )
        task_db: Task = result.scalar_one_or_none()
        if task_db:
            task_db.status = status
            now = datetime.now()
            if status == TaskStatus.RUNNING:
                task_db.started_at = now
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task_db.completed_at = now
                task_db.error = error
                task_db.result = task_result
            await self.db.commit()
            await self.db.refresh(task_db)
