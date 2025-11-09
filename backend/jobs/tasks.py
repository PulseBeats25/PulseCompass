import time


def long_task(seconds: int = 2) -> str:
    """Example long-running task.
    Simulates work by sleeping and returns a message.
    """
    for _ in range(max(1, seconds)):
        time.sleep(1)
    return f"Completed after {seconds} seconds"
