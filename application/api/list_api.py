from flask_restful import Resource, fields, marshal_with, reqparse
from ..models import User, Board, List
from datetime import datetime
from .api_validation import *
from application.database import db

EC = {
    'L01': '{board_id} is required and must be an integer',
    'L02': '{list_name} is required and must be a non-empty string between 4 and 50 characters',
    'L03': '{list_name} must be a non-empty string between 4 and 50 characters',
    'L04': 'Cannot delete list because it is not empty',
    'L05': 'Cannot move cards to a list which belongs to different board',
    'L06': 'Card is already in this list'
}

list_output_fields = {
    'list_id':      fields.Integer,
    'list_name':    fields.String,
    'created':      fields.DateTime(dt_format='iso8601') # rfc822, .strftime('%Y-%m-%d %H:%M:%S')
}

list_parser = reqparse.RequestParser()
list_parser.add_argument('board_id')
list_parser.add_argument('list_name')

class ListAPI(Resource):
    @marshal_with(list_output_fields)
    def post(self):
        args = list_parser.parse_args()
        bid = validate_int(args.get('board_id'), 'L01', EC['L01'])
        lname = validate_str(args.get('list_name'), 'L02', EC['L02'])
        board = Board.query.get(bid)
        if board is None:
            raise NotFoundError(entity='Board')
        try:
            new_list = List(list_name=lname, board_id=bid)
            db.session.add(new_list)
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()
            return List.query.get(new_list.list_id), 201

    @marshal_with(list_output_fields)
    def get(self, list_id):
        l = List.query.get(list_id)
        if l:
            return l, 200
        else:
            raise NotFoundError(entity='List')
    
    @marshal_with(list_output_fields)
    def put(self, list_id):
        l = List.query.get(list_id)
        if not l:
            raise NotFoundError(entity='List')
        
        args = list_parser.parse_args()
        lname = validate_str(args.get('list_name'), 'L03', EC['L03'])
        
        try:
            l.list_name = lname
        except:
            db.session.rollback()
        else:
            db.session.commit()
            return l, 200
        
    def delete(self, list_id):
        l = List.query.get(list_id)
        if not l:
            raise NotFoundError(entity='List')
        if l.cards != []:
            raise BusinessValidationError(status_code=400, error_code="L04", error_message=EC['L04'])
        else:
            try:
                db.session.delete(l)
            except:
                db.session.rollback()
            else:
                db.session.commit()
                return 'Successfully deleted', 200

class ListMoveDeleteAPI(Resource):
    def delete(self, list_id, mlist_id):
        l = List.query.get(list_id)
        mlist = List.query.get(mlist_id)

        if not l or not mlist:
            raise NotFoundError('List')
        
        if l.board != mlist.board:
            raise BusinessValidationError(status_code=400, error_code='L05', error_message=EC['L05'])
        
        if l == mlist:
            raise BusinessValidationError(status_code=400, error_code='L06', error_message=EC['L06'])

        try:
            for card in l.cards:
                card.list_id = mlist.list_id
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()

        try:
            db.session.delete(l)
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()
            return 'Successfully moved cards and deleted', 200
