from flask import request, redirect, url_for, render_template, flash, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from application.models import User
from application.validations import val_str
from main import bcrypt

#login
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('boards'))
        else:
            return render_template('index.html')
    
    if request.method == 'POST':
        uname = val_str(request.form.get('usr'), 4, 50, "Username must a string of length between 4 and 50 characters.") # len/null check
        pword = val_str(request.form.get('pwd'), 8, 20, "Password must have at least 8 characters and at most 20 characters.") # len/null check
        rembr = True if request.form.get('remember') == 'checked' else False
        if not uname or not pword: # if null or invalid length redirect
            return redirect(url_for('index'))
        user = User.query.filter_by(user_name=uname).first()
        if user:
            if bcrypt.check_password_hash(user.password, pword):
                login_user(user, remember=rembr)
                return redirect(url_for('boards'))
            else:
                flash('Incorrect password. Please check your password.')
                return render_template('index.html')
        else:
            flash('User not found. Please check your username.')
            return render_template('index.html')

#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
