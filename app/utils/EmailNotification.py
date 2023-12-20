import os

from flask_mail import Mail, Message
from flask import current_app

class EmailNotification:
    def __init__(self, app):
        self.mail = Mail(app)

    def send_email(self, subject, sender, recipients, body, pdf_paths=None):
        with current_app.app_context():
            msg = Message(subject, sender=sender, recipients=recipients)
            msg.body = body

            # Attach PDFs if provided
            if pdf_paths:
                for pdf_path in pdf_paths:
                    with open(pdf_path, 'rb') as pdf_file:
                        msg.attach(filename=os.path.basename(pdf_path),
                                   content_type='application/pdf',
                                   data=pdf_file.read())

            self.mail.send(msg)