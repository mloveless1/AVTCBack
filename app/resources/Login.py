import os

from bcrypt import checkpw
from dotenv import load_dotenv
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from flask_restful import Resource

if os.path.exists('.env'):
    load_dotenv()


# noinspection PyMethodMayBeStatic
class LoginResource(Resource):
    def post(self):
        user = request.json.get('username', None)
        user_pass = request.json.get('password', None)

        # Fetch the stored username and hashed password
        stored_username = os.getenv('USERNAME_TOKEN')
        stored_password_hash = os.getenv('PASSWORD')

        # Verify username and password
        if stored_username == user and checkpw(user_pass.encode(), stored_password_hash.encode()):
            # Create a new token with the user identity
            access_token = create_access_token(identity=user)
            return jsonify(access_token=access_token)
        else:
            return {'message': 'Bad credentials'}
