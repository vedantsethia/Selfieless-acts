def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%d-%m-%Y:%S-%M-%H')
        return True
    except ValueError:
        return False

from flask_cors import CORS
from flask import Flask, render_template, Response, request, jsonify
import pandas as pd
import os
import json
import shutil
import datetime
import base64
import binascii
import datetime



LOGIN_FILE_NAME = "login.csv"
DB = "templates/images" 
GLOBAL_LIST = "acts.csv"


app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/api/v1/users", methods = ['POST'])
def add_user():
    if request.method == 'POST':
        #print(request.data.decode('utf-8'))
        request_json =json.loads(request.data.decode('utf-8'))
        user_n = request_json['username']
        pwd = request_json['password']
        
        if not LOGIN_FILE_NAME in os.listdir():
            data = pd.DataFrame(columns = ['username', 'password'])
            data.to_csv(LOGIN_FILE_NAME, index = False)

        if not is_sha1(str(pwd)):
            return Response('{}', status=400, mimetype='application/json')

        data = pd.read_csv(LOGIN_FILE_NAME)
        if user_n in data['username'].tolist():
            return Response('{}', status=400, mimetype='application/json')

        data = data.append({'username': user_n, 'password': pwd}, ignore_index = True)
        data.to_csv(LOGIN_FILE_NAME, index = False)
        return Response('{}', status=200, mimetype='application/json')
         
    else:
        return Response('{}', status=405, mimetype='application/json')

    
@app.route("/api/v1/users/<username>", methods = ["DELETE"])
def remove_user(username = None):
    if request.method == 'DELETE':
        if not LOGIN_FILE_NAME in os.listdir():
            data = pd.DataFrame(columns = ['username', 'password'])
            data.to_csv(LOGIN_FILE_NAME, index = False)
        
        data = pd.read_csv(LOGIN_FILE_NAME)
        if username not in data['username'].tolist():
            return Response('{}', status=400, mimetype='application/json')

        data = data[data.username != username]
        data.to_csv(LOGIN_FILE_NAME, index = False)
        return Response('{}', status=200, mimetype='application/json')

    else:
        return Response('{}', status=405, mimetype='application/json')

		
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80, threaded=True)
    #app.run(threaded = True, debug = True)
