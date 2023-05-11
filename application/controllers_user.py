from flask import request, redirect, url_for, render_template, flash, current_app as app
from flask_login import login_required, logout_user, current_user
from application.models import User
from application.database import db
from application.validations import val_str
from main import bcrypt

#sign up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        uname = val_str(request.form.get('usr'), 4, 50, "Username must be between 4 and 50 characters long.") # len/null check
        pword = val_str(request.form.get('pwd'), 8, 20, "Password must be between 8 and 20 characters long.") # len/null check
        if not uname or not pword: # if null or invalid length redirect
            return redirect(url_for('signup'))
        user = User.query.filter_by(user_name=uname).first() # unique check
        if not user:
            try:
                hashed_pword = bcrypt.generate_password_hash(pword)
                new_user = User(user_name=uname, password=hashed_pword)
                db.session.add(new_user)
            except:
                db.session.rollback()
                return 'There was an error signing up.'
            else:
                db.session.commit()
                return redirect(url_for('index'))
        else:
            flash('Username is taken. Try a different one.')
            return redirect(url_for('signup'))

#rename
@app.route('/settings/change_name', methods=['GET', 'POST'])
@login_required
def change_user_name():
    if request.method == 'POST':
        uname = val_str(request.form.get('uname'), 4, 50, "Username must be between 4 and 50 characters long.") # len/null check
        try:
            if not uname: # if null or invalid length redirect
                return redirect(url_for('settings'))
            check_unique = User.query.filter_by(user_name=uname).first()
            if check_unique and current_user != check_unique: #unique check
                flash('Username is taken. Try a different one.')
                return redirect(url_for('settings'))
            elif check_unique and current_user == check_unique:
                flash('You have entered the same username')
                return redirect(url_for('settings'))
            else:
                current_user.user_name = uname
        except:
            db.session.rollback()
            return 'There was an error changing the user_name.'
        else:
            db.session.commit()
            flash('Username successfully changed.')
            return redirect(url_for('settings'))

# delete confirmation
@app.route('/settings/delete_confirmation', methods=['GET', 'POST'])
@login_required
def delete_confirmation():
    if request.method == 'GET':
        return render_template('del-confirm.html')
    
    if request.method == 'POST':
        choice = request.form.get('choice')
        if choice == 'no':
            return redirect(url_for('settings'))
        
        if choice == 'yes':
            try:
                db.session.delete(current_user)
            except:
                db.session.rollback()
                return 'There was an error deleting your account', 500
            else:
                db.session.commit()
            flash('Your account has been successfully deleted.')
            return redirect(url_for('index'))
