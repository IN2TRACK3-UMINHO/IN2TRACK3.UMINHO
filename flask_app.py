import os
import uuid
import json

import pandas as pd

from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()

from functools import wraps

from flask import Flask, render_template, request, redirect, session, jsonify, send_file

from handle_resquest import handle_prediction, handle_maintenance


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
    path = THIS_FOLDER / 'database/DataBase_In2Track3.csv'
    return send_file(path, as_attachment=True)

@app.route('/database/actionseffects')
def download_generic_actions():
    path = THIS_FOLDER / 'database/ActionsEffects.json'
    return send_file(path, as_attachment=True)

@app.route('/prediction')
@login_required
def prediction():
    path = THIS_FOLDER / 'database/markov.json'
    with open(path, "r") as file:
        markov_prediction = json.load(file)
    
    path = THIS_FOLDER / 'database/ActionsEffects.json'
    with open(path, "r") as file:
        maintenanceActions = json.load(file)
    
    return render_template('prediction.html', markov_prediction=markov_prediction, maintenanceActions=maintenanceActions)

@app.route('/maintenance', methods=['POST'])
@login_required
def maintenance_post():
    maintenance_scenario = json.loads(request.form['maintenanceScenario'])
    
    maintenance_prediction = handle_maintenance.get_IC_through_time_maintenance(maintenance_scenario)
    
    return maintenance_prediction

@app.route('/configuration', methods=['GET'])
@login_required
def setting_get():
    return render_template('configuration.html')

@app.route('/configuration', methods=['POST'])
@login_required
def setting_post():
    if ('inspectionsFile' in request.files):
        file = request.files['inspectionsFile']
        file.save(os.path.join('database', file.filename))
        update_markov()
        return ''
    
    if ('maintenanceFile' in request.files):
        file = request.files['maintenanceFile']
        file.save(os.path.join('database', file.filename))
        return ''
    
    return jsonify({'error': 'No file uploaded'}), 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

def update_markov():
    file_location = os.path.join('database', 'DataBase_In2Track3.csv')
    df  = pd.read_csv(file_location, sep=',')
    
    time_hoziron = 50
    markov_prediction = {}
    
    data_converted = handle_prediction.convert_to_markov(df[['Nome', 'Data',  'LL']], 3, 1, 'year')
    markov_LL = handle_prediction.get_fitted_markov_model(data_converted, 3, 1)
    
    markov_prediction['LL'] = list(markov_LL.theta)
    markov_prediction['LL_prediction'] = {'Time': list(range(0, time_hoziron + 1))}
    markov_prediction['LL_prediction']['IC'] = list(markov_LL.get_mean_over_time(time_hoziron))
    
    
    data_converted = handle_prediction.convert_to_markov(df[['Nome', 'Data',  'ALG']], 3, 1, 'year')
    markov_ALG = handle_prediction.get_fitted_markov_model(data_converted, 3, 1)
    
    markov_prediction['ALG'] = list(markov_ALG.theta)
    markov_prediction['ALG_prediction'] = {'Time': list(range(0, time_hoziron + 1))}
    markov_prediction['ALG_prediction']['IC'] = list(markov_ALG.get_mean_over_time(time_hoziron))
    

    
    # Writing
    path = THIS_FOLDER / 'database/markov.json'
    with open(path, "w") as file:
        file.write(json.dumps(markov_prediction,
                              indent=4))
    


if __name__ == '__main__':
    app.run(debug=True)
