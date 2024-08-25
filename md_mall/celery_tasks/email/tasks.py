from django.core.mail import send_mail
from celery_tasks.main import app
@app.task
def celery_send_email(subject, message, html_message,from_email, recipient_list):

    send_mail(subject=subject, message=message, html_message=html_message,
              from_email=from_email, recipient_list=recipient_list)