# Resource class for managing Parents
from flask_restful import Resource, reqparse, abort
import uuid


parent_parser = reqparse.RequestParser()
parent_parser.add_argument('parentName', type=str, required=True, help='Parent name is required')
parent_parser.add_argument('email', type=str, required=True, help='Email is required')
parent_parser.add_argument('phoneNumber', type=str, required=True, help='Phone number is required')
parent_parser.add_argument('athletes', type=list, location='json', default=[])

"""
class ParentResource(Resource):
    def get(self, parent_id):
        # Find and return the Parent by ID
        for parent in db['parents']:
            if parent['id'] == parent_id:
                return parent
        abort(404, message=f'Parent with ID {parent_id} not found')

    def put(self, parent_id):
        args = parent_parser.parse_args()
        # Find and update the Parent by ID
        for parent in db['parents']:
            if parent['id'] == parent_id:
                parent.update(args)
                return parent
        abort(404, message=f'Parent with ID {parent_id} not found')

    def delete(self, parent_id):
        # Find and delete the Parent by ID
        for parent in db['parents']:
            if parent['id'] == parent_id:
                db['parents'].remove(parent)
                return '', 204
        abort(404, message=f'Parent with ID {parent_id} not found') """