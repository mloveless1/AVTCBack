from .Index import Index
from .Athlete import AthleteResource
from .Login import LoginResource
from .Parent import ParentResource
from .Puller import PullerResource
from .Signup import SignupResource
from .DataExport import DataExport


def initialize_routes(api):
    api.add_resource(Index, '/')
    api.add_resource(AthleteResource, '/athletes/<int:athlete_id>')
    api.add_resource(LoginResource, '/login')
    api.add_resource(ParentResource, '/parent/<int:parent_id>')
    api.add_resource(PullerResource, '/puller')
    api.add_resource(SignupResource, '/signup')
    api.add_resource(DataExport, '/fetch_csv')

