import os
from flask import Flask, jsonify, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from celery import Celery

# Import your resources
from .database import db
from .resources import AthleteResource, ParentResource, SignupResource, LoginResource, PullerResource

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')


# Function to create Flask app
def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    JWTManager(app)
    Api(app).add_resource(LoginResource, '/login')
    Api(app).add_resource(AthleteResource, '/athletes/<int:athlete_id>')
    Api(app).add_resource(SignupResource, '/signup')
    Api(app).add_resource(ParentResource, '/parent/<int:parent_id>')
    Api(app).add_resource(PullerResource, '/puller')

    return app


# Initialize your Flask application
app = create_app()


# Initialize Celery
def make_celery(app):
    cel = Celery(app.import_name, broker='redis://localhost:6379/0')  # Adjust for your broker settings
    cel.conf.update(app.config)

    class ContextTask(cel.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    cel.Task = ContextTask
    return cel


celery = make_celery(app)

# Rest of your Flask app routes and functions
@app.route('/signin', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/fetch_csv', methods=['GET'])
def fetch_csv():
    return render_template('fetch_csv.html')


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = 'https://avtc-signup-front-aa5da244bd4a.herokuapp.com'
    header['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    header['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    header['Access-Control-Allow-Credentials'] = 'true'
    return response


if __name__ == '__main__':
    app.run()
