from flask import request, redirect, url_for, render_template, abort, current_app as app
from flask_login import login_required, current_user
from application.models import User, Board, List
from application.database import db
from application.validations import val_str

# ADD
@app.route('/dashboard/lists/<int:board_id>/new', methods=['GET', 'POST'])
@login_required
def add_list(board_id):
    if request.method == 'GET':
        return render_template('add-list.html', bid=board_id)

    if request.method == 'POST':
        lname = val_str(request.form.get('lname'), 4, 50, 'list_name must be between 4 and 50 characters long.') # len/null check
        if not lname: # if null or invalid length redirect
            return redirect(url_for('add_list', board_id=board_id))
        aboard = Board.query.get_or_404(board_id)
        try:
            new_list = List(list_name=lname)
            new_list.board = aboard
            db.session.add(new_list)
        except:
            db.session.rollback()
            return 'Error occured while adding list.', 500
        else:
            db.session.commit()
            return redirect(url_for('dashboard_lists', board_id=board_id))

# EDIT
@app.route('/dashboard/lists/<int:list_id>/edit', methods=['GET','POST'])
@login_required
def rename_list(list_id):
    if request.method == 'GET':
        rlist = List.query.get_or_404(list_id)
        bid = rlist.board.board_id
        return render_template('edit-list.html', rlist=rlist, bid=bid)

    if request.method == 'POST':
        ltitle = val_str(request.form.get('ltitle'), 4, 50, 'list_name must be between 4 and 50 characters long.') # len/null check
        if not ltitle:
            return redirect(url_for('rename_list', list_id=list_id))
        rlist = List.query.get_or_404(list_id)
        try:
            rlist.list_name = ltitle
        except:
            db.session.rollback()
            return 'An error occured while trying to rename the list.', 500
        else:
            db.session.commit()
            return redirect(url_for('dashboard_lists', board_id=rlist.board.board_id))

# DELETE
@app.route('/dashboard/lists/<int:list_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_list(list_id):
    if request.method == 'GET':
        dlist = List.query.get_or_404(list_id)
        bid = dlist.board.board_id
        try:
            db.session.delete(dlist)
        except:
            db.session.rollback()
            return 'Error occured while deleting the list.', 500
        else:    
            db.session.commit()
            return redirect(url_for('dashboard_lists', board_id=bid))

# MOVE & DELETE
@app.route('/dashboard/lists/<int:list_id>/move_delete/<int:mlist_id>', methods=['GET', 'POST'])
@login_required
def move_delete_list(list_id, mlist_id):
    if request.method == 'GET':
        dlist = List.query.get_or_404(list_id) # null check
        mlist = List.query.get_or_404(mlist_id) # null check
        if dlist.board != mlist.board: # if different lists then show 400 screen
            print('got here')
            abort(400, 'Cannot delete! Lists belong to different boards.')
        try:
            for card in dlist.cards:
                card.list_id = mlist_id
        except:
            db.session.rollback()
            return 'There was an error deleting the list.', 500
        else:
            db.session.commit()
            return redirect(url_for('delete_list', list_id=dlist.list_id))