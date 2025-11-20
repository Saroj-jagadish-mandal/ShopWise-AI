import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon_qa_project.settings')

app = Celery('amazon_qa_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

