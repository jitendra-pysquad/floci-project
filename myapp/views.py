from celery.result import AsyncResult
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .tasks import practice_redis_job


@ensure_csrf_cookie
def home(request):
    return render(request, "myapp/home.html")


def start_task(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    task = practice_redis_job.delay()
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
