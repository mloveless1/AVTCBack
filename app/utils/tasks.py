# tasks.py

from celery import current_app as celery_app
from flask_mail import Message, Mail
from flask import current_app


@celery_app.task(bind=True)
def send_async_email(self, subject, sender, recipients, body, pdf_paths=None):
    # Assuming Flask-Mail is initialized globally and app context issue is resolved
    with celery_app.app.app_context():  # Adjust based on your app context handling
        mail = Mail(current_app)
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = body

        if pdf_paths:
            for pdf_path in pdf_paths:
                with open(pdf_path, 'rb') as pdf_file:
                    msg.attach(filename=os.path.basename(pdf_path),
                               content_type='application/pdf',
                               data=pdf_file.read())
        mail.send(msg)
