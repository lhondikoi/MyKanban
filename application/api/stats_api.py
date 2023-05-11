from flask_restful import Resource, fields, marshal_with, reqparse
from ..models import User, Board, List
from datetime import datetime, timedelta
from .api_validation import *
from application.database import db

EC = {
    'S01': '{start_date} is required and must be in the format "yyyy-mm-dd"',
    'S02': '{end_date} is required and must be in the format "yyyy-mm-dd"',
    'S03': '{start_date} is before user_creation date',
    'S04': 'Date range cannot be greater than 84 days'
}

breakdown_output_fields = {
    'completed': fields.Integer,
    'pending': fields.Integer,
    'overdue': fields.Integer
}

timeline_output_fields = {
    'date': fields.String,
    'completed': fields.Integer
}

stats_parser = reqparse.RequestParser()
stats_parser.add_argument('start_date')
stats_parser.add_argument('end_date')

class BreakdownAPI(Resource):
    @marshal_with(breakdown_output_fields)
    def get(self, user_id):
        out = {
            "completed": 0,
            "pending": 0,
            "overdue": 0
        }
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('User')
        for board in user.boards:
            for l in board.lists:
                for card in l.cards:
                    if card.completed:
                        out['completed'] += 1
                    elif card.deadline and datetime.now() > card.deadline:
                        out['overdue'] += 1
                    else:
                        out['pending'] += 1
        return out, 200

class TimelineAPI(Resource):
    @marshal_with(timeline_output_fields)
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('User')
        args = stats_parser.parse_args()
        start_date = validate_date(args.get('start_date'), ecode='S01', emsg=EC['S01'])
        end_date = validate_date(args.get('end_date'), ecode='S02', emsg=EC['S02'])
        print(start_date, user.created.date())
        if start_date < user.created.date():
            raise BusinessValidationError(400, 'S03', EC['S03'])
        numdays = (end_date - start_date).days + 1
        if numdays > 84:
            raise BusinessValidationError(400, 'S04', EC['S04'])
        date_dict = {f'{start_date + timedelta(days=x)}': 0 for x in range(numdays)}
        for board in user.boards:
            for l in board.lists:
                for card in l.cards:
                    if card.completed and f'{card.completed_datetime.date()}' in date_dict:
                        date_dict[f'{card.completed_datetime.date()}'] += 1
        out = [{"date": d, "completed": c} for d, c in date_dict.items()]
        return out, 200
            