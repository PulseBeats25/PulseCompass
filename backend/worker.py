import os
import platform
from rq import Worker, Queue, SimpleWorker
from core.redis import get_redis

listen = ["default"]

if __name__ == "__main__":
    redis_conn = get_redis()
    queues = [Queue(name, connection=redis_conn) for name in listen]
    if platform.system().lower().startswith("win"):
        # Windows: use non-forking SimpleWorker
        worker = SimpleWorker(queues=queues, connection=redis_conn)
        worker.work()
    else:
        worker = Worker(queues=queues, connection=redis_conn)
        worker.work(with_scheduler=True)
