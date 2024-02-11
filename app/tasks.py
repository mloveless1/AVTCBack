# tasks.py
import os
from celery import current_app as celery_app
from flask_mail import Message
from flask import current_app
import logging


@celery_app.task(bind=True)
def send_async_email(self, subject, sender, recipients, body, pdf_paths=None):
    logging.info(f"Sending email to {recipients}")
    try:
        app = current_app._get_current_object()
        with app.app_context():
            mail = current_app.extensions.get('mail')
            msg = Message(subject, sender=sender, recipients=recipients, body=body)
            for pdf_path in (pdf_paths or []):
                with open(pdf_path, 'rb') as pdf_file:
                    msg.attach(filename=os.path.basename(pdf_path),
                               content_type='application/pdf',
                               data=pdf_file.read())
            mail.send(msg)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
