# tasks.py
import os
import logging
from celery import current_app as celery_app
from flask_mail import Message
from flask import current_app
from app.utils.ProcessPdf import ProcessPdf


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


@celery_app.task(bind=True)
def process_pdf_async(self, athlete_data, signature_img_path, template_path, output_file, x, y, width, height):
    temp_directory = '/tmp'  # Define your temp directory for PDFs
    try:
        # Initialize the PDF processor
        pdf_processor = ProcessPdf(temp_directory, output_file)

        # Add data to the PDF form
        pdf_processor.add_data_to_pdf(template_path, athlete_data)

        # Embed the signature image into the PDF
        # Note: Adjust x, y, width, height, and page_number as needed
        pdf_processor.embed_image_to_pdf(signature_img_path, os.path.join(temp_directory, output_file),
                                         x=x, y=y, width=width, height=height)

        logging.info(f"PDF processing complete for {athlete_data.get('full_name', 'Unknown')}")
    except Exception as e:
        logging.error(f"Error processing PDF for {athlete_data.get('full_name', 'Unknown')}: {e}")

