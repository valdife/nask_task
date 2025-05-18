import asyncio
from asyncio import sleep
from random import randint
from typing import Optional

from aiohttp import ClientSession

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.task import TaskStatus
from app.services.task_service import TaskService


@celery_app.task(name="long_task")
def long_task(task_id: str, callback_url: Optional[str] = None):
    asyncio.run(long_task_async(task_id, callback_url))


async def long_task_async(task_id: str, callback_url: Optional[str] = None):
    async with AsyncSessionLocal() as db:
        task_service = TaskService(db)
        try:
            await task_service.update_task_status(task_id, TaskStatus.RUNNING)

            await sleep(randint(10, 30))

            result = {"result": randint(9, 97)}
            await task_service.update_task_status(
                task_id, TaskStatus.COMPLETED, task_result=result
            )

            if callback_url:
                async with ClientSession() as session:
                    async with session.post(callback_url, json=result) as response:
                        response.raise_for_status()
        except Exception as e:
            await task_service.update_task_status(
                task_id, TaskStatus.FAILED, error=str(e)
            )
            raise
