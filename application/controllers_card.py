from flask import Flask, request, redirect, url_for, render_template, flash, current_app as app
from flask_login import login_required, current_user
from application.models import User, List, Card
from application.database import db
from application.validations import val_str, val_date
from datetime import datetime

# add
@app.route('/dashboard/cards/<int:list_id>/add', methods=['GET','POST'])
@login_required
def add_card(list_id):
    if request.method == 'GET':
        bid = List.query.get_or_404(list_id).board.board_id
        return render_template('add-card.html', lid=list_id, bid=bid)
    
    if request.method == 'POST':
        card_title = val_str(request.form.get('ctitle'), 4, 50, 'card_name must be between 4 and 50 characters long.') # len/null check
        if not card_title: # if null or invalid length redirect
            return redirect(url_for('add_card', list_id=list_id))
        content = request.form.get('description')
        deadline = val_date(request.form.get('deadline'))
        if deadline is False: # redirect if invalid format or less than current time
            return redirect(url_for('add_card', list_id=list_id))
        alist = List.query.get_or_404(list_id)
        if content == '':
            content = None
        try:
            new_card = Card(title=card_title, content=content, deadline=deadline, completed_datetime=None)
            db.session.add(new_card)
            new_card.list = alist
        except:
            db.session.rollback()
            return 'An error occured while adding the card.', 500
        else:
            db.session.commit()
            return redirect(url_for('dashboard_lists', board_id=new_card.list.board.board_id))

# edit
@app.route('/dashboard/cards/<int:card_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_card(card_id):
    if request.method == 'GET':
        card = Card.query.get_or_404(card_id)
        bid = card.list.board.board_id
        return render_template('edit-card.html', card=card, bid=bid)
    
    if request.method == 'POST':
        ctitle = val_str(request.form.get('ctitle'), 4, 50, 'card_name must be between 4 and 50 characters long.') #len/null check
        if not ctitle: # if null or invalid length redirect
            return redirect(url_for('edit_card', card_id=card_id))
        content = request.form.get('description')
        deadline = val_date(request.form.get('deadline'))
        ecard = Card.query.get_or_404(card_id)
        if content == '':
            content = None
        if deadline is False: # redirect if invalid format or less than current time
            return redirect(url_for('edit_card', card_id=card_id))
        try:
            if deadline:
                ecard.title, ecard.content, ecard.deadline = ctitle, content, deadline
            else:
                ecard.title, ecard.content = ctitle, content
        except:
            db.session.rollback()
            return 'There was an error updating the card.', 500
        else:
            db.session.commit()
            return redirect(url_for('dashboard_lists', board_id=ecard.list.board.board_id))

# mark complete
@app.route('/dashboard/cards/<int:card_id>/mark', methods=['POST'])
@login_required
def comp_card(card_id):
    if request.method == 'POST':
        comp = True if request.form.get('comp') == 'checked' else False
        ccard = Card.query.get_or_404(card_id)
        bid = ccard.list.board.board_id
        try:
            if comp:
                ccard.completed = True
                ccard.completed_datetime = datetime.now()
            else:
                ccard.completed = False
                ccard.completed_datetime = None
        except:
            db.session.rollback()
            return 'There was an error updating the card.', 500
        else:
            db.session.commit()
            return redirect(url_for('dashboard_lists', board_id=bid))

# move to different list
@app.route('/dashboard/cards/<int:card_id>/move/<int:list_id>')
@login_required
def move_card(card_id, list_id):
    if request.method == 'GET':
        mcard = Card.query.get_or_404(card_id)
        mlist = List.query.get_or_404(list_id)
        bid = mlist.board.board_id
        if mcard.list.board != mlist.board:
            flash('List belongs to a different board.')
            return redirect(url_for('dashboard_lists', board_id=mcard.list.board.board_id))
        try:
            mcard.list_id = list_id
        except:
            db.session.rollback()
            return 'There was an error moving the card.', 500
        else:
            db.session.commit()
            return redirect(url_for('dashboard_lists', board_id=bid))

# DELETE
@app.route('/dashboard/cards/<int:card_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_card(card_id):
    if request.method == 'GET':
        dcard = Card.query.get_or_404(card_id)
        bid = dcard.list.board.board_id
        try:
            db.session.delete(dcard)
        except:
            db.session.rollback()
            return 'There was an error deleting the card.', 500
        else:
            db.session.commit()
            return redirect(url_for('dashboard_lists', id=id, board_id=bid))