from .database import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)                        # PK
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    
    # user <-1-----n-> board
    boards = db.relationship('Board', backref='user', cascade='all, delete')

class Board(db.Model):
    __tablename__ = 'board'
    board_id = db.Column(db.Integer, primary_key=True)      # PK
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))      # FK
    board_name = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    
    # board <-1-----n-> list
    lists = db.relationship('List', backref='board', cascade='all, delete')

class List(db.Model):
    __tablename__ = 'list'
    list_id = db.Column(db.Integer, primary_key=True)                   # PK
    board_id = db.Column(db.Integer, db.ForeignKey('board.board_id'))   # FK
    list_name = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    
    # list <-1-----n-> card
    cards = db.relationship('Card', backref='list', cascade='all, delete')

class Card(db.Model):
    __tablename__ = 'card'
    card_id = db.Column(db.Integer, primary_key=True)                   # PK
    list_id = db.Column(db.Integer, db.ForeignKey('list.list_id'))      # FK
    created = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.now)
    
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    completed_datetime = db.Column(db.DateTime, default=None)