from flask import Flask, render_template, request, url_for, redirect, abort, jsonify, make_response
from flask_cors import CORS, cross_origin
import sqlite3 as sql
import hashlib
import json
import re
import requests
import ast
app = Flask(__name__)
cor2 = CORS(app, resources={r"/api/v1/categories": {"origins": "*"}})
cor3 = CORS(app, resources={r"/api/v1/acts": {"origins": "*"}})
cor4 = CORS(app, resources={r"/api/v1/acts/upvote": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
msg =""

count =0
crash =0
#home page
@app.route('/api/v1')
def home():
   r = requests.get('http://3.208.210.43:6600/api/v1/users')
   s = ast.literal_eval(r.text)
   print(s)
   return s[2]
   

		
# 3)list all categories on front-end
@app.route('/api/v1/categories', methods=['GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def list_categories():
         global count,crash 
         count = count + 1
         if crash == 1:
                  return jsonify({}),500          
         elif request.method == 'GET':
                  con = sql.connect("/data/cloud_db.db")
                  con.row_factory = sql.Row
                  cur = con.cursor()
                  cur.execute("PRAGMA foreign_keys = ON")
                  cur.execute("SELECT * FROM CATEGORIES")
                  rows = cur.fetchall()
                  if not rows:
                     return jsonify({}),204
                  tasks = {}
                  for row in rows:
                        tasks[row['CATEGORY_NAME']]=row['NUM_OF_ACTS']
                  return jsonify(tasks),200
                  #return render_template("categories.html",rows=rows),200
         else:
                  return jsonify({}),405

# 4)add new category
@app.route('/api/v1/categories',methods = ['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def add_category():
	global count,crash 
	count = count + 1
	if crash == 1:
		return jsonify({}),500
	elif request.method == 'POST':
		python_dict = request.get_json()
		category_name = python_dict[0]
		with sql.connect("/data/loud_db.db") as con:
			cur = con.cursor()
			cur.execute("PRAGMA foreign_keys = ON")
			cur.execute("SELECT CATEGORY_NAME FROM CATEGORIES")
			rows = cur.fetchall() #returns tuple of tuples
			for row in rows:
				if(row[0] == category_name):
					msg = "Category already exists"
					return jsonify({}),400
			
			cur.execute("INSERT INTO CATEGORIES (CATEGORY_NAME,NUM_OF_ACTS) VALUES (?,?)",(category_name,0))
			con.commit()
		msg = "Category successfully added"
		return jsonify({}),201
	else:
		return jsonify({}),405		


# 5)delete category
@app.route('/api/v1/categories/<category_name>',methods = ['DELETE','GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def delete_categories(category_name):
	global count,crash 
	count = count + 1
	if crash == 1:
			return jsonify({}),500
	elif request.method == 'DELETE':
		with sql.connect("/data/cloud_db.db") as con:
			cur = con.cursor()
			cur.execute("PRAGMA foreign_keys = ON")
			cur.execute("SELECT CATEGORY_NAME FROM CATEGORIES")
			rows = cur.fetchall() #returns tuple of tuples
			for row in rows:
				if(row[0] == category_name):
					cur.execute("DELETE FROM CATEGORIES WHERE CATEGORY_NAME=?", (category_name,)) #specify name as tuple
					con.commit()
					msg = "Category successfully deleted!"
					return jsonify({}),200

			msg = "Category does not exist!"
			return jsonify({}),400
	else:
		msg="Category could not be deleted!"
		return jsonify({}), 405
		
		

# 6) and 8) list acts for a given category
@app.route('/api/v1/categories/<category_name>/acts', methods=['GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def list_acts_for_category(category_name):
	global count,crash 
	count = count + 1
	start = request.args.get('start',None)
	end = request.args.get('end',None)
	con = sql.connect("/data/cloud_db.db")
	con.row_factory = sql.Row
	cur = con.cursor()
	cur.execute("PRAGMA foreign_keys = ON")
	cur.execute("SELECT * FROM CATEGORIES")
	rows = cur.fetchall() #returns tuple of tuples
	if crash == 1:
		return jsonify({}),500
	elif request.method == 'GET':
	
		if not start and not end:
	
			for row in rows:
		
				if(row[0] == category_name):
		
					if(row[1] == 0):
						msg="Category has no acts"
						return jsonify({}),204
					
					elif(row[1]<=100):
				
						cur2=con.cursor()
						cur2.execute("SELECT * FROM ACTS WHERE category=? ORDER BY TIME_STAMP DESC",(category_name,))
				
						rows2 = cur2.fetchall()
						acts=[]
						for row2 in rows2:
							act={}
							st = row2['TIME_STAMP']
							st2 = st[:11] + st[-2:] + st[-6:-2] + st[-8:-6]
							act['actId']=row2['ACT_ID']
							act['username']=row2['username']
							act['timestamp']=st2
							act['caption']=row2['CAPTION']
							act['upvotes']=row2['UPVOTES']
							act['categoryName']=row2['category']
							act['imgB64']=row2['IMGB64']
							acts.append(act)
						return jsonify(acts),200
					else:
						msg="No.of acts is greater than 100, could not show."
						return jsonify({}),413
		
			msg="Category does not exist"
			return jsonify({}),204
		else:
			if not start or not end:
				msg="Range parameter is missing"
				return jsonify({}),204
			else:
				for row in rows:

					if(row[0] == category_name):
				
						if(row[1] == 0):
							msg="Category has no acts"
							return jsonify({}),204
					
						elif(int(start)>=1 and int(end)<=row[1] and int(start)<=int(end)):
							
							if(int(end) -int(start)+1<=100):
				
								cur2=con.cursor()
								cur2.execute("SELECT * FROM ACTS WHERE category=? ORDER BY TIME_STAMP DESC",(category_name,))
								rows2 = cur2.fetchall()
								acts=[]
								i=0
								for row2 in rows2:							
									i=i+1
									if(i >= int(start) and i <= int(end)):
										st = row2[1]
										st2 = st[:11] + st[-2:] + st[-6:-2] + st[-8:-6]
										act={}
										act['actId']=row2['ACT_ID']
										act['username']=row2['username']
										act['timestamp']=st2
										act['caption']=row2['CAPTION']
										act['upvotes']=row2['UPVOTES']
										act['categoryName']=row2['category']
										act['imgB64']=row2['IMGB64']
										acts.append(act)
								return jsonify(acts),200
							else:
								msg="request too large"
								return jsonify({}),413
						else:
							msg="not in range"
							return jsonify({}),400	
				msg="Category does not exist"
				return jsonify({}),204

	else:
		return jsonify({}),405
		
		
# 7)list number of acts for a given category
@app.route('/api/v1/categories/<category_name>/acts/size',methods=['GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def number_of_acts(category_name):
	global count,crash 
	count = count + 1
	if crash == 1:
		return jsonify({}),500
	elif request.method == 'GET':
		con = sql.connect("/data/cloud_db.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("PRAGMA foreign_keys = ON")
		cur.execute("SELECT * FROM CATEGORIES")
		rows = cur.fetchall() #returns tuple of tuples
	
		for row in rows:
		
			if(row[0] == category_name):
				return jsonify([row[1]]),200
		msg="Category does not exist"
		return jsonify([]),400
					
	else:
		msg="Method not allowed"
		return jsonify({}),405

			
# 9)UPVOTE AN ACT
@app.route('/api/v1/acts/upvote',methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def upvote():	
	global count,crash 
	count = count + 1
	if crash == 1:
		return jsonify({}),500
	elif request.method == 'POST':
		python_dict = request.get_json()
		act_id = python_dict[0]
		with sql.connect("/data/cloud_db.db") as con:
			cur = con.cursor()
			cur.execute("PRAGMA foreign_keys = ON")
			cur.execute("SELECT * FROM ACTS")
			rows = cur.fetchall() #returns tuple of tuples
			for row in rows:
				if(row[0] == int(act_id)):
					#print(type(row[3]))
					cur.execute("UPDATE ACTS SET UPVOTES=UPVOTES+1 WHERE ACT_ID=?",(act_id,))
					return jsonify({}),200
			msg = "act id not found"
			return jsonify({}),400
	else:
		msg = "method not allowed"
		return jsonify({}),405
		
	
# 10)REMOVE AN ACT
@app.route('/api/v1/acts/<act_id>', methods=['DELETE','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def delete_act(act_id):
	global count,crash 
	count = count + 1
	if crash == 1:
		return jsonify({}),500
	elif request.method == 'DELETE':
		with sql.connect("/data/cloud_db.db") as con:
				cur = con.cursor()
				cur.execute("PRAGMA foreign_keys = ON")
				cur.execute("SELECT * FROM ACTS")
				rows = cur.fetchall()
				
				for row in rows:
					if(row[0] == int(act_id)):
						
						cur.execute("DELETE FROM ACTS WHERE ACT_ID=?", (act_id,)) #specify name as tuple
						cur.execute("UPDATE CATEGORIES SET NUM_OF_ACTS=NUM_OF_ACTS -1 WHERE CATEGORY_NAME=?", (row[6],))
						con.commit()
						msg = "Act successfully deleted!"
						return jsonify({}),200

				msg = "Act_id does not exist!"
				return jsonify({}),400
	else:
		msg="Act could not be deleted!"

@app.route('/api/v1/_count',methods = ['DELETE', 'GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def count_request():
        global count,crash
        if crash == 1:
				return jsonify({}),500
        elif request.method == 'GET':
                return jsonify([count]),200
        elif request.method == 'DELETE':
                count = 0
                return jsonify([count]),200
        else:
                return jsonify({}),405
	
	
# 11)upload acts
@app.route('/api/v1/acts', methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def upload_act():
	global count,crash 
	count = count + 1
	if crash == 1:
		return jsonify({}),500
	elif request.method=='POST':
		python_dict = request.get_json()
		act_id = python_dict['actId']
		flag=0
		flg=0
		with sql.connect("/data/cloud_db.db") as con:
			cur = con.cursor()
			cur.execute("PRAGMA foreign_keys = ON")
			cur.execute("SELECT ACT_ID FROM ACTS")
			rows = cur.fetchall() #returns tuple of tuples
			for row in rows:
				if(row[0] == int(act_id)):
					msg = "Act id already exists"
					return jsonify({}),400
			
			cur2 = con.cursor()
			cur2.execute("PRAGMA foreign_keys = ON")
			cur2.execute("SELECT CATEGORY_NAME FROM CATEGORIES")
			rows2 = cur2.fetchall() #returns tuple of tuples
			for row2 in rows2:
				if(row2[0] == python_dict['categoryName']):
					msg = "Category already exists"
					flag=1
					break
			r = requests.get('http://52.22.130.148:8080/api/v1/users',headers={"origin":"54.83.67.154"})
			s = ast.literal_eval(r.text)	
			#cur3 = con.cursor()
			#cur3.execute("PRAGMA foreign_keys = ON")
			#cur3.execute("SELECT USERNAME FROM USERS")
			#rows3 = cur3.fetchall() #returns tuple of tuples
			for row3 in s:
				if(row3 == python_dict['username']):
					msg = "User already exists"
					flg=1
					break
			
			time = re.search("(0[1-9]|([12][0-9])|(3[01]))[-](0[1-9]|1[012])[-]([0-9]{4}):[0-5][0-9][-][0-5][0-9][-](([0-1][0-9])|(2[0-3]))$",python_dict['timestamp'])
			image = re.search("([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$",python_dict['imgB64'])
			if(time == None):
				msg = "timestamp not in DD-MM-YYYY:SS-MM-HH format"
				return jsonify({}),400
			y=image.group(0)
			if(y != python_dict['imgB64']):
				msg = "not in base64"
				return jsonify({}),400
			if(flag==1 and flg==1 and len(python_dict) == 6):
				st = python_dict['timestamp']
				st2 = st[:11] + st[-2:] + st[-6:-2] + st[-8:-6]
				cur.execute("INSERT INTO ACTS (ACT_ID,TIME_STAMP,CAPTION,UPVOTES,IMGB64,username,category) VALUES (?,?,?,?,?,?,?)",(act_id,st2,python_dict['caption'],0,python_dict['imgB64'],python_dict['username'],python_dict['categoryName']))
				cur.execute("UPDATE CATEGORIES SET NUM_OF_ACTS=NUM_OF_ACTS +1 WHERE CATEGORY_NAME=?", (python_dict['categoryName'],))
				con.commit()
				msg = "Act successfully uploaded"
				return jsonify({}),201
			else:
				msg="more than 6 columns"
				return jsonify({}),400
	
	else:
		msg = "Method not allowed"
		return jsonify({}),405
	



@app.route('/api/v1/acts/count', methods=['GET','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def count_act():
	global count,crash
	 
	count = count + 1
	if crash == 1:
		return jsonify({}),500
	elif request.method == 'GET':
		con = sql.connect("/data/cloud_db.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("PRAGMA foreign_keys = ON")
		cur.execute("SELECT * FROM CATEGORIES")
		rows = cur.fetchall() #returns tuple of tuples
		sum1 = 0	
		for row in rows:
			sum1 = sum1 + row[1]
		return jsonify([sum1]),200
					
	else:
		msg="Method not allowed"
		return jsonify({}),405

@app.route('/api/v1/_crash', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def crash_server():
      if request.method == 'POST':   
         global crash
         crash = 1
         return jsonify({}),200
      else:
            msg = "Method Not Allowed"
            return jsonify({}),405

@app.route('/api/v1/_health', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def health_check():
      if request.method == 'GET':   
         global crash
         if crash == 1:
            return jsonify({}),500
         else:
            try:
               con = sql.connect("/data/cloud_db.db")
               con.row_factory = sql.Row
               cur = con.cursor()
               cur.execute("PRAGMA foreign_keys = ON")
               cur.execute("SELECT * FROM ACTS")
               cur.execute("SELECT * FROM CATEGORIES")
               return jsonify({}),200
            except Exception as e:
               msg = "exception in query"
               return jsonify(msg),500
            
      else:
            msg = "Method Not Allowed"
            return jsonify({}),405
	
if __name__ == '__main__':
   app.run(host="0.0.0.0",debug = True,port=80)
