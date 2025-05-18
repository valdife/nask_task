from asyncio import sleep

from app.core.celery_app import celery_app


@celery_app.task
async def long_task(task_id: str):
    await sleep(10)
    return {
        "task_id": task_id,
        "status": "completed",
    }
