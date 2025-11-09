"""
Metrics Router - Observability endpoints for monitoring
"""
from fastapi import APIRouter
from rq import Queue
from core.redis import get_redis
from datetime import datetime

router = APIRouter()


@router.get("/metrics/queues")
async def queue_metrics():
    """Get queue statistics for monitoring"""
    try:
        redis_conn = get_redis()
        queue = Queue("default", connection=redis_conn)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "queues": {
                "default": {
                    "name": queue.name,
                    "count": len(queue),
                    "started_count": queue.started_job_registry.count,
                    "finished_count": queue.finished_job_registry.count,
                    "failed_count": queue.failed_job_registry.count,
                    "deferred_count": queue.deferred_job_registry.count,
                    "scheduled_count": queue.scheduled_job_registry.count,
                }
            }
        }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "queues": {}
        }


@router.get("/metrics/workers")
async def worker_metrics():
    """Get worker statistics"""
    try:
        from rq import Worker
        redis_conn = get_redis()
        workers = Worker.all(connection=redis_conn)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "worker_count": len(workers),
            "workers": [
                {
                    "name": w.name,
                    "state": w.get_state(),
                    "current_job": w.get_current_job_id(),
                    "successful_jobs": w.successful_job_count,
                    "failed_jobs": w.failed_job_count,
                }
                for w in workers
            ]
        }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "worker_count": 0,
            "workers": []
        }
