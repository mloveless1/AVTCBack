from flask import make_response, render_template
from flask_restful import Resource


# noinspection PyMethodMayBeStatic
class DataExport(Resource):
    def get(self):
        return make_response(render_template('fetch_csv.html'), 200, {'Content-Type': 'text/html'})
