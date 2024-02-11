# tasks.py

from celery import current_app as celery_app
from flask_mail import Message
from flask import current_app


@celery_app.task(bind=True)
def send_async_email(subject, sender, recipients, body, pdf_paths=None):
    # Retrieve the Flask app instance
    app = current_app._get_current_object()
    with app.app_context():
        # Access the pre-initialized Mail instance
        mail = current_app.extensions.get('mail')
        msg = Message(subject, sender=sender, recipients=recipients, body=body)

        # Attach PDFs if provided
        if pdf_paths:
            for pdf_path in pdf_paths:
                with open(pdf_path, 'rb') as pdf_file:
                    msg.attach(filename=os.path.basename(pdf_path),
                               content_type='application/pdf',
                               data=pdf_file.read())

        mail.send(msg)
