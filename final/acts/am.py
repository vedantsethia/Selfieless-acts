import boto3
from flask import Flask,request,make_response
from flask import jsonify
from boto3.dynamodb.conditions import Key, Attr
import decimal
import flask.json
import json
import re
import base64
import requests
from flask_cors import CORS

session = boto3.Session(
    aws_access_key_id="AKIAIB3EEP4PWMLE66SA",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)

# app = Flask(__name__)
r_count=0
health=1

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

def datematch(s):
    pattern = re.compile('^(0?[1-9]|[12][0-9]|3[01])\-(0?[1-9]|1[0-2])\-\d\d\d\d:(0[0-9]|[0-5][0-9])\-([0-9]|[0-5][0-9])\-(0[0-9]|1[0-9]|2[0-3])$')
    m=pattern.match(s)
    if m:
        return False
    else:
        return True

def isBase64(s):
	return True
	try:
		return base64.b64encode(base64.b64decode(s)) == s
	except Exception:
		return False

#############################################################################################################

#3...categories 4..add a cateory
#done
@app.route("/api/v1/categories",methods=['GET','POST'])
def categories():
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=='GET'):
		r_count+=1
		response = table1.scan()
		if(int(response['Count'])==0):
			return make_response(jsonify({ }),204)
		else:#implement like dictionary	
			dat=dict()
			li=[]
			for i in response['Items']:
				dat[i['category_name']]=int(i['acts'])
			li.append(dat)
			print(li)
			return jsonify(li[0]),200
	elif(request.method=='POST'):
		r_count+=1
		cat=request.data.decode('utf-8')
		if cat[0]!= '[' or cat[-1]!=']':
			return "",400
		name=cat[2:-2]
		fe = Key('category_name').eq(name)
		response = table1.scan(
			 FilterExpression=fe
			)
		if(int(response['Count'])>0):
			return make_response("",400)
		else:
			table1.put_item(
			Item={
				'category_name': name,
				'acts': 0
				}
			)
			return make_response(jsonify({ }),201)
	else:
		return make_response("",405)

#############################################################################

#5...remove a category
#done
@app.route("/api/v1/categories/<categoryName1>",methods=['DELETE'])
def removecat(categoryName1):
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=="DELETE"):
		r_count+=1
		fe = Key('category_name').eq(categoryName1)
		response = table1.scan(		
				 FilterExpression=fe
		)
		if(response['Count']>0):
			fe1 = Key('categoryName').eq(categoryName1)
			response = table2.scan(
				FilterExpression=fe1
			)
			for i in response['Items']:
				table2.delete_item(
				Key={
				'actid': int(i['actid'])
				}
				)
    		################################	
			table1.delete_item(
			Key={
				'category_name': categoryName1
				}
			)
			return make_response(jsonify({ }),200)
		else:
			return make_response("",400)
	else:
		return make_response("Bad request",405)
    
##################################################################################
#6...List acts 
#8 implemented here
#done
@app.route("/api/v1/categories/<categoryName>/acts",methods=['GET','POST'])
def listacts(categoryName):
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=="GET"):
		st=request.args.get('start')
		ed=request.args.get('end')
		if(st and ed):
			r_count+=1
			if((int(ed)-int(st))>100):
				return "",413
			else:
				fe = Key('category_name').eq(categoryName)
				response = table1.scan(
					FilterExpression=fe
				)
				if(response['Count']>0):
					fe = Key('categoryName').eq(categoryName)
					response = table2.scan(
						FilterExpression=fe
					)
					print(response)
					if(int(response['Count'])==0):
						return make_response(jsonify({ }),204)
					else:
						response=response["Items"]
						di=dict()
						for i in response:
							j=i['timestamp'].split(":")
							j1=j[0].split("-")
							j2=j[1].split("-")
							di[j1[2]+j1[1]+j1[0]+j2[2]+j2[1]+j2[0]+str(int(i['actid']))]=i
						li=[]
						for key in sorted(di):
							li.append(di[key])
						li=li[::-1]
						le=len(li)
						if(int(ed)>le):
							return "index out of range",400
						li=li[int(st):int(ed)+1]
						#print(li)
						return make_response(jsonify(li),200)
				else:
					return make_response("",400)
		else:
			r_count+=1
			fe = Key('category_name').eq(categoryName)
			response = table1.scan(
				FilterExpression=fe
			)
			if(response['Count']>0):
				fe = Key('categoryName').eq(categoryName)
				response = table2.scan(
					FilterExpression=fe
				)
				print(response['Count'])
				if(int(response['Count'])==0):
					return make_response(jsonify({ }),204)
				elif(int(response['Count'])>=100):
					return make_response(jsonify({ }),413)
				else:	
					di=dict()
					for i in response["Items"]:
						j=i['timestamp'].split(":")
						j1=j[0].split("-")
						j2=j[1].split("-")
						di[j1[2]+j1[1]+j1[0]+j2[2]+j2[1]+j2[0]+str(int(i['actid']))]=i
						i['actid']=int(i['actid'])
						i['upvote']=int(i['upvote'])
					li=[]
					for key in sorted(di):
						li.append(di[key])
					#print(li)
					return jsonify(li[::-1]),200

			else:
				return make_response("",400)
	else:
		return make_response("Bad request",405)


##################################################################################
#7.... size of acts
@app.route("/api/v1/categories/<categoryName>/acts/size",methods=['GET'])
def sizeacts(categoryName):
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=="GET"):
		r_count+=1
		fe = Key('category_name').eq(categoryName)
		response = table1.scan(
			FilterExpression=fe
		)
		if(response['Count']>0):
			fe = Key('categoryName').eq(categoryName)
			response = table2.scan(
				FilterExpression=fe
				)
			ls=[response['Count']]
			return make_response(json.dumps(ls),200) 
		else:
			return make_response("",400)
	else:
		return make_response("Bad request",405)

#####################################################################################
#9...Upvote an act
@app.route("/api/v1/acts/upvote",methods=['POST','GET'])
def upvote():
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=="POST"):
		r_count+=1
		actid=request.data.decode('utf-8')
		if actid[0]!= '[' or actid[-1]!=']':
			return "here",400
		actid=actid[1:-1]
		try:
			actid=int(actid)
		except:
			return make_response("invalid",400)
		try:
			response = table2.update_item(
				Key={'actid':int(actid)},
				UpdateExpression="set upvote=upvote+ :val",
				ExpressionAttributeValues={
					':val': 1
				},
				ReturnValues="UPDATED_NEW"
			)
			return make_response(jsonify({ }),200)
		except:
			return make_response("sdcsad",400)
	else:
		return make_response("Bad request",405)
#######################################################################################
#10...remove an act
@app.route("/api/v1/acts/<actid>",methods=['DELETE'])
def remove(actid):
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=="DELETE"):
		r_count+=1
		fe = Key('actid').eq(int(actid))
		response = table2.scan(
			FilterExpression=fe
		)
		if(response['Count']>0):
			response=response["Items"][0]
			cat=response['categoryName']
			response = table1.update_item(
				Key={'category_name':cat},
				UpdateExpression="set acts=acts- :val",
				ExpressionAttributeValues={
					':val': 1
				},
				ReturnValues="UPDATED_NEW"
			)
			table2.delete_item(
				Key={
					"actid":int(actid)
				}
			)
			return make_response(jsonify({ }),200) 
		else:
			return make_response("act_id not found",400)
	else:
		return make_response("Bad request",405)
##############################################################################################

#11th apis
@app.route("/api/v1/acts",methods=['GET','POST'])
def upload():
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=="POST"):
		r_count+=1
		content = request.get_json(force=True)
		#print(content)
		act_id=int(content['actId'])
		name=content['username']
		tims=content['timestamp']
		caption=content['caption']
		cat_nam=content['categoryName']
		img64=content['imgB64']
		if(datematch(tims)):
			print("time inncorrect")
			return "time inncorrect",400
		try:
			if(content['upvotes']):	
				print("upvotes passed")
				return "upvotes passed",400
		except:
			try:
				imgB64_byte = img64.encode('utf-8')
				if(isBase64(imgB64_byte)==False):
					print("Failed because of image base64 issue")
					return jsonify({}),400
				response = table2.scan()
				for i in response['Items']:
					if(int(i['actid'])==act_id):
						print("actsid exists")
						return "actsid exists",400
				fe = Key('username').eq(name)
				ss=requests.get("http://3.212.102.137:80/api/v1/users")
				if(ss.status_code!=200):
					print("error fetching users")
					return "error fetching users",400
				if(name not in ss.json()):
					print("Invalid user")
					return "Invalid user",400
				fe = Key('category_name').eq(cat_nam)
				response2 = table1.scan(
					FilterExpression=fe
				)
				if(response2['Count']>0):
					response = table1.update_item(
						Key={'category_name':cat_nam},
						UpdateExpression="set acts=acts+ :val",
						ExpressionAttributeValues={
							':val': 1
						},
						ReturnValues="UPDATED_NEW"
					)
					table2.put_item(
						Item={
							'actid':int(act_id),
							'timestamp':tims,
							'caption':caption,
							'categoryName':cat_nam,
							'upvote':0,
							'username':name,
							'imgB64':img64
							}
						)
					return make_response(jsonify({ }),201)
				else:
					print("username or categoryName problem")
					return "username or categoryName problem",400
			except:
				print("Image not in correct from")
				return "Image not in correct from",400
	else:
		return make_response("Bad request",405)
#######################################################################################################
@app.route("/api/v1/acts/count",methods=['GET'])
def sizeacts1():
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=="GET"):
		r_count+=1
		response = table2.scan(
		)
		ls=[response['Count']]
		return make_response(json.dumps(ls),200)
	else:
		return make_response("Bad request",405)

#############################################################################################################
@app.route("/api/v1/_count",methods=['GET','DELETE'])
def sizeacts111():
	global r_count
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	if(request.method=="GET"):
		ls=[r_count]
		return make_response(json.dumps(ls),200)
	elif(request.method=="DELETE"):
		r_count=0
		return make_response(jsonify({ }),200)
	else:
		return make_response("Bad request",405)
########################################################################################################

@app.route("/api/v1/_health",methods=['GET'])
def sizeacts1111():
	global health
	if(health==1):
		return make_response(jsonify({ }),200)
	else:
		return make_response(jsonify({ }),500)

########################################################################################################
@app.route("/api/v1/_crash",methods=['POST'])
def sizeacts1csc111():
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	else:
		health=0
		return make_response(jsonify({ }),200)
#######################################################################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=80)