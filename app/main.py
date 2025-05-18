import uuid
from asyncio import sleep
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.task import Task, TaskStatus
from app.services.task_service import TaskService
from app.tasks.long_task import long_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/task/{task_id}")
async def get_task(task_id: str) -> EventSourceResponse:
    async def event_generator():
        async with AsyncSessionLocal() as db:
            task_service = TaskService(db)
            while True:
                task = await task_service.get_task(task_id)
                if not task:
                    yield {"event": "error", "data": "Task not found"}
                    break

                await db.refresh(task)

                yield {
                    "event": "status",
                    "data": {
                        "status": task.status.value,
                        "result": task.result,
                        "error": task.error,
                    },
                }

                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    break

                await sleep(5)

    return EventSourceResponse(event_generator())


@app.post("/task")
async def create_task(callback_url: Optional[str] = None) -> dict[str, str]:
    task_id = str(uuid.uuid4())
    db: AsyncSession
    async with AsyncSessionLocal() as db:
        long_task.apply_async(kwargs={"task_id": task_id, "callback_url": callback_url})
        task_status = Task(
            id=task_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            callback_url=callback_url,
        )
        db.add(task_status)
        await db.commit()

    return {"task_id": task_id}
