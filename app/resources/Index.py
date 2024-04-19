from flask_restful import Resource


# noinspection PyMethodMayBeStatic
class Index(Resource):
    def get(self):
        return {'message': 'You don\'t belong in the index, go ahead and go somewhere else'}, 200