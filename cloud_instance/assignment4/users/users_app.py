from flask import Flask, render_template, request, url_for, redirect, abort, jsonify, make_response
from flask_cors import CORS, cross_origin
import sqlite3 as sql
import hashlib
import json
import re
app = Flask(__name__)
cors = CORS(app, resources={r"/api/v1/users": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
msg =""
#home page
@app.route('/api/v1')
def home():
   return render_template('selfie_home.html')
   
"""@app.route('/enternew')
def new_student():
   return render_template('student.html')"""

count = 0
# 1)add new user
@app.route('/api/v1/users',methods = ['POST', 'GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def add_user():
	global count
	count = count + 1
	if request.method == 'POST':
		python_dict = request.get_json()
		
		#return str(python_dict)
		#encrypted_password = hashlib.sha1(python_dict['password'].encode()).hexdigest()
		with sql.connect("/data/cloud_db.db") as con:
			cur = con.cursor()
			cur.execute("PRAGMA foreign_keys = ON")
			cur.execute("SELECT USERNAME FROM USERS")
			rows = cur.fetchall() #returns tuple of tuples
			for row in rows:
				if(row[0] == request.json['username']):
					msg = "User already exists"
					return  jsonify({}),400
			x = re.search("[a-fA-F0-9]{40}$",request.json['password'])
			if (x == None):
				msg = "password not in sha1"
				return  jsonify({}),400
				
			cur.execute("INSERT INTO USERS (USERNAME,PASSWORD) VALUES (?,?)",(python_dict['username'],python_dict['password']))
			con.commit()
		msg = "User successfully added"
		return jsonify({}),201
		
	elif request.method == 'GET':
		with sql.connect("/data/cloud_db.db") as con:
			cur = con.cursor()
			cur.execute("PRAGMA foreign_keys = ON")
			cur.execute("SELECT USERNAME FROM USERS")
			rows = cur.fetchall()
			users = []
			for row in rows:
				users.append(row[0])
			return jsonify(users),200
	else:
		return jsonify({}),405	
		
	
	
# 2)delete user
@app.route('/api/v1/users/<username>',methods = ['DELETE','GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def delete_user(username):
	global count
	count = count + 1
	if request.method == 'DELETE':
		with sql.connect("/data/cloud_db.db") as con:
			cur = con.cursor()
			cur.execute("SELECT USERNAME FROM USERS")
			rows = cur.fetchall() #returns tuple of tuples
			for row in rows:
				if(row[0] == username):
					cur.execute("PRAGMA foreign_keys = ON")
					cur.execute("DELETE FROM USERS WHERE USERNAME=?", (username,)) #specify name as tuple
					#cur.execute("DELETE FROM USERS WHERE USERNAME=?", (username,))
					con.commit()
					msg = "User successfully deleted!"
					return  jsonify({}),200

			msg = "User does not exist!"
			return  jsonify({}),400
	else:
		msg="User could not be deleted!"
		return jsonify({}), 405

@app.route('/api/v1/_count',methods = ['DELETE', 'GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def count_request():
	global count
	if request.method == 'GET':
		return jsonify([count]),200	
	elif request.method == 'DELETE':
		count = 0
		return jsonify([count]),200
	else:
		return jsonify({}),405


		
	
if __name__ == '__main__':
   app.run(host='0.0.0.0',debug = True,port=5000)
