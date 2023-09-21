import uuid
import json

import pandas as pd

from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()

from functools import wraps

from flask import Flask, render_template, request, redirect, session, jsonify, send_file

app = Flask(__name__)
app.secret_key = 'your_secret_key1'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated_function
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username and password are valid
        if username == 'IN2TRACK3_UMINHO' and password == 'IN2TRACK3_UMINHO_123':
            session['logged_in'] = True
            return redirect('/home')
        else:
            return 'Invalid login credentials'
    return render_template('login.html')

@app.route('/')
@app.route('/home')
@login_required
def index():
    return render_template('home.html')

@app.route('/database/genericdatabase')
def download_generic_csv():
    path = THIS_FOLDER / 'database/GenericDataBase.csv'
    return send_file(path, as_attachment=True)

@app.route('/database/actionseffect')
def download_generic_actions():
    path = THIS_FOLDER / 'database/ActionsEffects.json'
    return send_file(path, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
