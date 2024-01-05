from .Athlete import AthleteResource
from .Parent import ParentResource
from .Signup import SignupResource
import os
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

database_uri = os.getenv('DATABASE_URL')