import pytest
from .mock_data import VALID_SIGNUP_DATA
from flask_testing import TestCase
from app.app import create_app, db
from app.models import Parent, Athlete
from unittest.mock import patch


class TestSignupResource(TestCase):

    def create_app(self):
        # Return a Flask app configured for testing
        return create_app(testing=True)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @patch('myapp.routes.SignupResource.send_async_email')
    def test_successful_signup(self, mock_send_email):
        # Mock send_async_email to do nothing on call
        mock_send_email.return_value = None

        # Example data for a successful signup
        data = VALID_SIGNUP_DATA

        response = self.client.post('/signup', json=data)

        assert response.status_code == 201
        assert response.json['message'] == 'Sign up successful'
        assert Parent.query.count() == 1
        assert Athlete.query.count() == 1
        mock_send_email.assert_called_once()

    def test_missing_required_fields(self):
        data = {
            # 'parentName': 'John Doe',  # Intentionally omitted
            'email': 'john@example.com',
            'phoneNumber': '1234567890',
            'athletes': []
        }
        response = self.client.post('/signup', json=data)
        assert response.status_code == 400
        assert 'parentName' in response.json['message']  # Assuming the response contains info about missing fields

    def test_invalid_email_format(self):
        data = {
            'parentName': 'John Doe',
            'email': 'not-an-email',
            'phoneNumber': '1234567890',
            'athletes': [{
                'athleteFullName': 'Jane Doe',
                'dateOfBirth': '2010-05-01',
                'gender': 'female',
                'returner_status': True,
            }],
            'signature': 'valid-base64-data'
        }
        response = self.client.post('/signup', json=data)
        assert response.status_code == 400
        assert 'email' in response.json['message']

    def test_invalid_signature_data(self):
        # Setup test data with invalid base64 signature
        data = {
            'parentName': 'John Doe',
            'email': 'john@example.com',
            'phoneNumber': '1234567890',
            'athletes': [
                {
                    'athleteFullName': 'Jane Doe',
                    'dateOfBirth': '2010-05-01',
                    'gender': 'female',
                    'returner_status': True,
                }
            ],
            'signature': 'invalid-base64-data',
        }

        response = self.client.post('/signup', json=data)

        # Expecting a 500 error due to invalid base64 data handling
        assert response.status_code == 500
        assert 'Error saving signature image' in response.json['message']

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_filesystem_error_saving_signature(self, mock_open):
        data = {
            # Valid signup data
        }

        response = self.client.post('/signup', json=data)

        assert response.status_code == 500
        assert 'Error saving signature image' in response.json['message']

    @patch('myapp.routes.SignupResource.send_async_email')
    @patch('myapp.utils.ProcessPdf.ProcessPdf.add_data_to_pdf')
    def test_pdf_generation_and_email_sending(self, mock_add_data_to_pdf, mock_send_email):
        mock_send_email.return_value = None
        mock_add_data_to_pdf.return_value = None

        data = {
            'subject': 'X signed up',
            'sender': 'malc.loveless@gmail.com',
            'recipients': 'jack@gmail.com',
            'body': 'X signed up',
            'pdf_paths': ''

        }

        response = self.client.post('/signup', json=data)

        assert response.status_code == 201
        mock_add_data_to_pdf.assert_called()
        mock_send_email.assert_called_once_with(
            subject=data['subject'],
            sender=data['sender'],
            recipients=data['recipients'],
            body=data['body'],
            pdf_paths=data['pdf_paths']
        )
