from flask import request, redirect, url_for, render_template, abort, current_app as app
from flask_login import login_required, current_user
from application.models import User, Board
from application.stats import *
from datetime import datetime, timedelta
import json

# usermenu
@app.route('/settings')
@login_required
def settings():
    if request.method == 'GET':
        return render_template('view_user.html', user=current_user)

# boardview
@app.route('/dashboard/boards')
@login_required
def boards():
    if request.method == 'GET':
        return render_template('view_board.html', user=current_user)

# listview -- check if user has boards
@app.route('/dashboard/lists')
@login_required
def lists():
    if request.method == 'GET':
        if current_user.boards == []:
            return render_template('view_list.html', user=current_user, dboard=False)
        else:
            return redirect(url_for('dashboard_lists', board_id=current_user.boards[0].board_id))

# listview -- atleast one board
@app.route('/dashboard/lists/<int:board_id>')
@login_required
def dashboard_lists(board_id):
    if request.method == 'GET':
        dboard = Board.query.get_or_404(board_id)
        if dboard in current_user.boards:   #IMP: checks if board belongs to user
            clist = {}
            for l in dboard.lists:
                tasks = len(l.cards)
                comp = 0
                for card in l.cards:
                    if card.completed == True:
                        comp += 1
                clist[l.list_id] = comp, tasks
            return render_template('view_list.html', user=current_user, dboard=dboard, clist=clist)
        else:
            return redirect(url_for('boards'))

# stats page
@app.route('/dashboard/stats', methods=['GET', 'POST'])
@login_required
def dashboard_stats():
    if request.method == 'GET':
        data = {"user": current_user}
        data["stats_for"] = 'user'
        if data['user'].boards != []:
            data["stats"] = basic_stats('user', current_user.id)
            ct = request.args.get('custom_timeline')
            if data['stats']['cards'] != 0:
                data["empty_user"] = False
                if ct is None:
                    make_timeline('user', current_user.id, data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
                else:
                    try:
                        sd, ed = [datetime.strptime(x, '%Y-%m-%d').date() for x in ct.split('_to_')]
                        numdays = (ed-sd).days + 1
                        if 7 <= numdays <= 21:
                            make_timeline('user', current_user.id, data['stats']['completed'], sd, numdays)
                        else:
                            make_timeline('user', current_user.id,  data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
                    except:
                        make_timeline('user', current_user.id,  data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
            else:
                data["empty_user"] = True
        else:
            data["empty_user"] = True
        return render_template('view_stats.html', **data)
    
    if request.method == 'POST':
        data = {"user": current_user}
        data["stats_for"], data["stats_of"] = [val for key, val in json.loads(request.form.get('get_stats')).items()]
        if data["stats_for"] == 'board':
            board = Board.query.get_or_404(data['stats_of'])
            if board.lists != []:
                data['entity'] = board
                data['stats'] = basic_stats('board', data["stats_of"])
                ct = request.args.get('custom_timeline')
                if data['stats']['cards'] != 0:
                    data["empty_board"] = False
                    if ct is None:
                        make_timeline('board', data['stats_of'], data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
                    else:
                        try:
                            sd, ed = [datetime.strptime(x, '%Y-%m-%d').date() for x in ct.split('_to_')]
                            numdays = (ed-sd).days + 1
                            if 7 <= numdays <= 21:
                                make_timeline('board', data['stats_of'], data['stats']['completed'], sd, numdays)
                            else:
                                make_timeline('board', data['stats_of'],  data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
                        except:
                            make_timeline('board', data['stats_of'],  data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
                else:
                    data['empty_board'] = True
            else:
                data['empty_board'] = True
            return render_template('view_stats.html', **data)
        
        if data["stats_for"] == 'list':
            l = List.query.get_or_404(data["stats_of"])
            if l.cards != []:
                data['empty_list'] = False
                data['entity'] = l
                data['stats'] = basic_stats('list', data["stats_of"])
                ct = request.args.get('custom_timeline')
                if ct is None:
                    make_timeline('list', data['stats_of'], data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
                else:
                    try:
                        sd, ed = [datetime.strptime(x, '%Y-%m-%d').date() for x in ct.split('_to_')]
                        numdays = (ed-sd).days + 1
                        if 7 <= numdays <= 21:
                            make_timeline('list', data['stats_of'], data['stats']['completed'], sd, numdays)
                        else:
                            make_timeline('list', data['stats_of'],  data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
                    except:
                        make_timeline('list', data['stats_of'],  data['stats']['completed'], datetime.now().date() - timedelta(days=3), 7)
            else:
                data['empty_list'] = True
            return render_template('view_stats.html', **data)