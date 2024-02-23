import os
import logging
from celery import Celery
from dotenv import load_dotenv
from flask_mail import Message
from flask import current_app
from app.utils.ProcessPdf import ProcessPdf

if os.path.exists('.env'):
    load_dotenv()

celery = Celery(__name__, broker=os.getenv("REDIS_URL"), backend=os.getenv("REDIS_URL"))


@celery.task
def send_async_email(subject: str, sender: str, recipients: str, body: str, pdf_paths: list = None) -> None:
    logging.info(f"Sending email to {recipients}")
    try:
        with current_app.app_context():
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


@celery.task
def process_pdf_async(athlete_data, signature_img_path, template_path, output_file, x, y, width, height):
    temp_directory = '/tmp'  # heroku directory for files
    path_to_pdf = os.path.join(temp_directory, output_file)
    try:
        # Initialize the PDF processor
        pdf_processor = ProcessPdf(temp_directory, output_file)

        # Add data to the PDF form
        pdf_processor.add_data_to_pdf(template_path, athlete_data)

        # Embed the signature image into the PDF
        # Note: Adjust x, y, width, height
        pdf_processor.embed_image_to_pdf(signature_img_path, path_to_pdf,
                                         x=x, y=y, width=width, height=height)

        logging.info(f"PDF processing complete for {athlete_data.get('PlayersName', 'Unknown')}")
    except Exception as e:
        logging.error(f"Error processing PDF for {athlete_data.get('PlayersName', 'Unknown')}: {e}")
