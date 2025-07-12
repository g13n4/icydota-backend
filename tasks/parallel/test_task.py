from celery import shared_task

@shared_task(name="test_task_task", ignore_result=True)
def test_task_task():
    print("Hello world")
