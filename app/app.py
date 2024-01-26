<<<<<<< HEAD
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from .database import db
from .resources import AthleteResource, ParentResource
=======
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
# from .database import init_db
from flask_cors import CORS
from .resources import AthleteResource, ParentResource, PullerResource, LoginResource
>>>>>>> 99be4270c8c81035629328f9f6ec72b81fc7deaf
from .resources import SignupResource

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # to suppress a warning message
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

db.init_app(app)

# Run DB setup
# init_db.setup_database()

# Flask-Mail Configs
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'malcolmloveless@gmail.com'
app.config['MAIL_PASSWORD'] = 'jcch wzuz wblr bhtl'

jwt = JWTManager(app)

api.add_resource(LoginResource, '/login')
api.add_resource(AthleteResource, '/athletes/<int:athlete_id>')
api.add_resource(SignupResource, '/signup')
api.add_resource(ParentResource, '/parent/<int:parent_id>')
api.add_resource(PullerResource, '/puller')



@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = 'https://avtc-signup-front-aa5da244bd4a.herokuapp.com'
    header['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    header['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    header['Access-Control-Allow-Credentials'] = 'true'
    return response
<<<<<<< HEAD
=======


if __name__ == '__main__':
    app.run()
>>>>>>> 99be4270c8c81035629328f9f6ec72b81fc7deaf
