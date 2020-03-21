import boto3
from flask import Flask,request,make_response
from flask import jsonify
from boto3.dynamodb.conditions import Key, Attr
import decimal
import flask.json
import json
import re
import base64
from flask_cors import CORS

session = boto3.Session(
    aws_access_key_id="AKIAIB3EEP4PWMLE66SA",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)

# app = Flask(__name__)
r_count=0

dynamodb = session.resource('dynamodb')
table = dynamodb.Table('users')
table1 = dynamodb.Table('categories')
table2 = dynamodb.Table('acts')
app = Flask(__name__)
CORS(app)

class MyJSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to strings.
            return str(obj)
        return super(MyJSONEncoder, self).default(obj)
app.json_encoder = MyJSONEncoder

def isValidSha1(s):
    pattern = re.compile("^[a-fA-F0-9]{40}$")
    m=pattern.match(s)
    if m:
        return False
    else:
        return True

########################################################################

#1...user and passoword update
@app.route("/api/v1/users",methods=['POST','GET'])
def hello():
	global r_count
	if(request.method=="POST"):
		r_count+=1
		content = request.get_json()
		fe = Key('username').eq(content['username'])
		response = table.scan(
			 FilterExpression=fe
			)#sha1 check here
		if(int(response['Count'])>0):
			return make_response("",400)
		elif(isValidSha1(content['password'])):
			return make_response("",400)
		else:
			table.put_item(
			Item={
				'username': content['username'],	
				'pass': content['password'],
			}
			)
			return make_response(jsonify({ }),201)
	elif(request.method=="GET"):
		try:
			r_count+=1
			response = table.scan()
			if(int(response['Count'])==0):
				return make_response("no users found",204)
			ls=[i['username'] for i in response['Items']]
			return make_response(json.dumps(ls),200) 
		except Exception as e:
			print("exception : ", e)
	else:
		return make_response("",405)

###########################################################################
#2...delete user
@app.route("/api/v1/users/<username>",methods=['DELETE'])
def removeuser(username):
	global r_count
	if(request.method=="DELETE"):
		r_count+=1
		fe = Key('username').eq(username)
		response = table.scan(		
				 FilterExpression=fe
		)
		if(int(response['Count'])>0):
			table.delete_item(
			Key={
				'username': username,
			}
			)
			return make_response(jsonify({ }),200)
		else:
			return make_response("",400)
	else:
		return make_response("",405)

#####################################################################################
@app.route("/api/v1/_count",methods=['GET','DELETE'])
def sizeacts11():
	global r_count
	if(request.method=="GET"):
		ls=[r_count]
		return make_response(json.dumps(ls),200)
	elif(request.method=="DELETE"):
		r_count=0
		return make_response(jsonify({ }),200)
	else:
		return make_response("Bad request",405)
############################################################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)