from flask import Flask, request, redirect, url_for, render_template, current_app as app

# 404
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', e='404', msg='The requested resource was not found.'), 404

# 400
@app.errorhandler(400)
def bad_request(error):
    return render_template('error.html', e='400', msg=error.description), 400