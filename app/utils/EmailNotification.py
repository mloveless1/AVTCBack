from flask_mail import Message
from flask import current_app
import os


class EmailNotification:
    def __init__(self):
        # Assuming Mail has been initialized with the app and attached to current_app
        self.mail = current_app.extensions.get('mail')

    def send_email(self, subject, sender, recipients, body, pdf_paths=None):
        # No need to manually push app context here, assuming this method is called within a Flask view function
        msg = Message(subject, sender=sender, recipients=recipients, body=body)

        # Attach PDFs if provided
        if pdf_paths:
            for pdf_path in pdf_paths:
                with open(pdf_path, 'rb') as pdf_file:
                    msg.attach(filename=os.path.basename(pdf_path),
                               content_type='application/pdf',
                               data=pdf_file.read())

        self.mail.send(msg)
