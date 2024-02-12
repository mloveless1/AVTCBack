from .routes import initialize_routes
from .Login import LoginResource
from .Athlete import AthleteResource
from .Parent import ParentResource
from .Signup import SignupResource
from .Puller import PullerResource
import os
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')
