from flask import request, redirect, url_for, render_template, current_app as app
from flask_login import login_required, current_user
from application.models import User, Board
from application.database import db
from application.validations import val_str

# ADD
@app.route('/dashboard/boards/new', methods=['GET', 'POST'])
@login_required
def add_board():
    if request.method == 'GET':
        return render_template('add-board.html')
    
    if request.method == 'POST':
        bname = val_str(request.form.get('bname'), 4, 50, 'board_name must be between 4 and 50 characters long.') # len/null check
        if not bname: # if null or invalid length redirect
            return redirect(url_for('add_board'))
        try:
            new_board = Board(board_name=bname)
            new_board.user = current_user
            db.session.add(new_board)
        except:
            db.session.rollback()
            return 'An error occured while creating a board.', 500
        else:
            db.session.commit()
            return redirect(url_for('boards'))

# RENAME
@app.route('/dashboard/boards/<int:board_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_board(board_id):
    if request.method == 'GET':
        board = Board.query.get_or_404(board_id)
        return render_template('edit-board.html', board=board)
    
    if request.method == 'POST':
        bname = val_str(request.form.get('bname'), 4, 50, 'board_name must be between 4 and 50 characters long.') #len/null check
        if not bname: # if null or invalid length redirect
            return redirect(url_for('edit_board'))
        rboard = Board.query.get_or_404(board_id)
        try:
            rboard.board_name = bname
        except:
            db.session.rollback()
            return 'There was an error renaming the board.', 500
        else:
            db.session.commit()
            return redirect(url_for('boards'))

# DELETE
@app.route('/dashboard/boards/<int:board_id>/delete')
@login_required
def delete_board(board_id):
    if request.method == 'GET':
        board = Board.query.get_or_404(board_id)
        try:
            db.session.delete(board)
        except:
            db.session.rollback()
            return 'There was an error deleting the board.', 500
        else:
            db.session.commit()
            return redirect(url_for('boards'))