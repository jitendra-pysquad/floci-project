import logging

from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from kombu.exceptions import OperationalError

from .tasks import practice_redis_job

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def home(request):
    return render(request, "myapp/home.html")


def start_task(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        task = practice_redis_job.delay()
    except OperationalError:
        logger.exception("Could not connect to the Celery broker while queueing task")
        return JsonResponse(
            {
                "error": "Django could not connect to the Celery broker. Check Redis and CELERY_BROKER_URL on the server."
            },
            status=503,
        )
    except Exception:
        logger.exception("Could not queue Celery task")
        return JsonResponse(
            {"error": "Django could not queue the Celery task. Check the server logs for details."},
            status=500,
        )

    return JsonResponse({"task_id": task.id})


def task_status(request, task_id):
    task = AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "state": task.state,
        "ready": task.ready(),
    }

    if isinstance(task.info, dict):
        response.update(task.info)
    elif task.failed():
        response["message"] = str(task.info)

    return JsonResponse(response)


def celery_health(request):
    try:
        connection = practice_redis_job.app.connection_for_write()
        connection.ensure_connection(max_retries=1)
        connection.release()
    except Exception:
        logger.exception("Celery broker health check failed")
        return JsonResponse({"ok": False, "error": "Celery broker is not reachable."}, status=503)

    return JsonResponse({"ok": True})
