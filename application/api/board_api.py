from flask_restful import Resource, fields, marshal_with, reqparse
from ..models import User, Board, List
from datetime import datetime
from .api_validation import *
from application.database import db

EC = {
    'B01': '{user_id} is required and must be an integer',
    'B02': '{board_name} is required and must be a non-empty string between 4 and 50 characters',
    'B03': '{board_name} must be a non-empty string between 4 and 50 characters',
    'B04': 'Cannot delete board because it is not empty'
}

board_output_fields = {
    'board_id':      fields.Integer,
    'board_name':    fields.String,
    'created':      fields.DateTime(dt_format='iso8601') # rfc822, .strftime('%Y-%m-%d %H:%M:%S')
}

board_parser = reqparse.RequestParser()
board_parser.add_argument('user_id')
board_parser.add_argument('board_name')

class BoardAPI(Resource):
    @marshal_with(board_output_fields)
    def post(self):
        args = board_parser.parse_args()
        uid = validate_int(args.get('user_id'), 'B01', EC['B01'])
        bname = validate_str(args.get('board_name'), 'B02', EC['B02'])
        user = User.query.get(uid)
        if not user:
            raise NotFoundError(entity='User')
        try:
            new_board = Board(board_name=bname, user_id=uid)
            db.session.add(new_board)
        except:
            db.session.rollback()
            raise InternalServerError()
        else:
            db.session.commit()
            return new_board, 201

    @marshal_with(board_output_fields)
    def get(self, board_id):
        board = Board.query.get(board_id)
        if board:
            return board, 200
        else:
            raise NotFoundError(entity='Board')
    
    @marshal_with(board_output_fields)
    def put(self, board_id):
        board = Board.query.get(board_id)
        if not board:
            raise NotFoundError(entity='Board')
        
        args = board_parser.parse_args()
        bname = validate_str(args.get('board_name'), 'B03', EC['B03'])
        
        try:
            board.board_name = bname
        except:
            db.session.rollback()
        else:
            db.session.commit()
            return board, 200
        
    def delete(self, board_id):
        board = Board.query.get(board_id)
        if not board:
            raise NotFoundError(entity='Board')
        if board.lists != []:
            raise BusinessValidationError(status_code=400, error_code="B04", error_message=EC['B04'])
        else:
            try:
                db.session.delete(board)
            except:
                db.session.rollback()
            else:
                db.session.commit()
                return 'Successfully deleted', 200