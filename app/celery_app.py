from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",  #broker queue
    backend="redis://localhost:6379/1",  #storing result
    include=["app.tasks.email_tasks"]
)

celery_app.conf.update(
    task_serializer="json",   #Serialization format
    autoretry_for=(ConnectionError,Exception, ),  #if failed retry if this is the case
    retry_backoff=True,  #if its network or service problem retry after sometime
    max_retries=3, #retry only 3 times 
    result_expiry=3600 #redis result backend expiry
)