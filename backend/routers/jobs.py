from fastapi import APIRouter, Depends
from rq import Queue
from core.redis import get_redis
from core.auth import get_current_user
from jobs.tasks import long_task

router = APIRouter()

@router.post("/jobs/parse")
async def enqueue_parse(_: dict = Depends(get_current_user)):
    q = Queue("default", connection=get_redis())
    job = q.enqueue(long_task, 2)
    return {"job_id": job.get_id()}

@router.get("/jobs/{job_id}")
async def job_status(job_id: str, _: dict = Depends(get_current_user)):
    q = Queue("default", connection=get_redis())
    job = q.fetch_job(job_id)
    if not job:
        return {"status": "not_found"}
    return {"status": job.get_status(), "result": job.result}
