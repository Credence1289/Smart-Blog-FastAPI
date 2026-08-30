from app.celery_app import celery_app
from app.utils.email_utils import first_post_congrats_email, password_reset_link, welcome_email

@celery_app.task
def send_password_reset_email(to_email:str, reset_token:str):
    password_reset_link(to_email, reset_token)


@celery_app.task
def send_welcome_email(to_email:str, name:str):
    welcome_email(to_email, name)


@celery_app.task
def send_first_post_congrats_email(to_email:str, name:str, post_title:str):
    first_post_congrats_email(to_email, name, post_title)