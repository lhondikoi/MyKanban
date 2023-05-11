from flask import request, redirect, url_for, render_template, current_app as app
from flask_login import login_required, current_user
from application.models import User, Board, List
from application.stats import *
from application.database import db
from datetime import datetime

# get user timeline
@app.route('/dashboard/<int:id>/stats/user_timeline', methods=['GET', 'POST'])
@login_required
def user_timeline(id):
    if request.method == 'POST':
        if User.query.get_or_404(id).is_authenticated:
            sd = request.form.get('start_date')
            ed = request.form.get('end_date')
            cl = basic_stats('user', id)['completed']
            if sd and ed:
                sd = datetime.strptime(sd, '%Y-%m-%d').date()
                ed = datetime.strptime(ed, '%Y-%m-%d').date()
                numdays = (ed-sd).days + 1
                if 7 <= numdays <= 28:
                    make_timeline('user', id, cl, sd, numdays)
                return redirect(url_for('dashboard_stats', id=id, custom_timeline=f'{sd}_to_{ed}'))
            else:
                return redirect(url_for('dashboard_stats', id=id))

# get board timeline
@app.route('/dashboard/<int:board_id>/stats/board_timeline', methods=['GET', 'POST'])
@login_required
def board_timeline(board_id):
    if request.method == 'POST':
        if Board.query.get(board_id).user.is_authenticated:
            sd = request.form.get('start_date')
            ed = request.form.get('end_date')
            cl = basic_stats('board', board_id)['completed']
            if sd and ed:
                sd = datetime.strptime(sd, '%Y-%m-%d').date()
                ed = datetime.strptime(ed, '%Y-%m-%d').date()
                numdays = (ed-sd).days + 1
                if 7 <= numdays <= 28:
                    make_timeline('board', board_id, cl, sd, numdays)
                return redirect(url_for('dashboard_stats', id=Board.query.get(board_id).user.id, custom_timeline=f'{sd}_to_{ed}'))
            else:
                return redirect(url_for('dashboard_stats', id=Board.query.get(board_id).user.id))

# get list timeline
@app.route('/dashboard/<int:list_id>/stats/list_timeline', methods=['GET', 'POST'])
def list_timeline(list_id):
    if request.method == 'POST':
        if List.query.get(list_id).board.user.is_authenticated:
            sd = request.form.get('start_date')
            ed = request.form.get('end_date')
            cl = basic_stats('list', list_id)['completed']
            if sd and ed:
                sd = datetime.strptime(sd, '%Y-%m-%d').date()
                ed = datetime.strptime(ed, '%Y-%m-%d').date()
                numdays = (ed-sd).days + 1
                if 7 <= numdays <= 28:
                    make_timeline('list', list_id, cl, sd, numdays)
                return redirect(url_for('dashboard_stats', id=List.query.get(list_id).board.user.id, custom_timeline=f'{sd}_to_{ed}'))
            else:
                return redirect(url_for('dashboard_stats', id=List.query.get(list_id).board.user.id))