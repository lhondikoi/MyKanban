import os
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(LocalDevelopmentConfig)

db.init_app(app)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
bcrypt = Bcrypt(app)
app.app_context().push()

# login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# importing controllers
from application.controllers_user import *
from application.controllers_board import *
from application.controllers_list import *
from application.controllers_card import *
from application.controllers_view import *
from application.controllers_stats import *
from application.controllers_error import *
from application.controllers_login import *
from application.controllers_reports import *

# importing restful api
from application.api.list_api import ListAPI, ListMoveDeleteAPI
from application.api.card_api import CardAPI, CardMoveAPI
from application.api.board_api import BoardAPI
from application.api.stats_api import BreakdownAPI, TimelineAPI

# adding resources
api.add_resource(ListAPI, '/api/list','/api/list/<int:list_id>')
api.add_resource(ListMoveDeleteAPI, '/api/list/move_delete/<int:list_id>/<int:mlist_id>')
api.add_resource(CardAPI, '/api/card','/api/card/<int:card_id>')
api.add_resource(CardMoveAPI, '/api/card/move/<int:card_id>/<int:list_id>')
api.add_resource(BreakdownAPI, '/api/stats/breakdown/<int:user_id>')
api.add_resource(TimelineAPI, '/api/stats/timeline/<int:user_id>')
api.add_resource(BoardAPI, '/api/board','/api/board/<int:board_id>')

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000
    )