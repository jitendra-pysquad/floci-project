import time

from celery import shared_task


@shared_task(bind=True)
def practice_redis_job(self):
    total_steps = 5

    for step in range(1, total_steps + 1):
        time.sleep(1)
        self.update_state(
            state="PROGRESS",
            meta={
                "current": step,
                "total": total_steps,
                "message": f"Processing step {step} of {total_steps}",
            },
        )

    return {
        "current": total_steps,
        "total": total_steps,
        "message": "Celery finished the Redis-backed practice job.",
    }
