from flask import Flask, render_template, request, redirect, abort, jsonify
import threading
import requests
import time, signal, sys
import docker
import json

"""
ip = "http://52.44.111.126:"
apis =	['/api/v1/_count',
		'/api/v1/_health',
		'/api/v1/_crash',
		'/api/v1/categories',
		'/api/v1/categories/<categoryName>/acts/size',
		'/api/v1/categories/<categoryName>/acts',
		'/api/v1/categories/<categoryName>',  	
		'/api/v1/acts/count',
		'/api/v1/acts/upvote',
		'/api/v1/acts/<actId>',
		'/api/v1/acts']
"""
		
app = Flask(__name__)
sem = threading.Semaphore()

containers = []
nexxt = -1
size = 0
tot_reqs = 0
client = docker.from_env()

def getnexxt():  #loadb
	global nexxt, containers, vv
	nexxt = (nexxt + 1) % size
	return containers[nexxt]["port"]

def startnewcontainer(port, idx):
	global client, size, containers
	cont = client.containers.run("acts", detach=True, ports={'80/tcp': port})
	if idx < size:
		containers[idx] = {'id':cont.id, 'port':port}
	else:
		containers.append({'id':cont.id, 'port':port})
	print(client.containers.list())
	time.sleep(5)
	size += 1
		
def stopcontainer(idx):
	global size, client
	client.containers.get(containers[idx]['id']).stop()
	size -= 1

def delete():
	global containers
	print("\ndestroying containers")
	for ii, i in enumerate(containers):
		stopcontainer(ii)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>',methods=['POST','GET','DELETE'])
def hello(path):
	global apis, size, tot_reqs, sem
	path = '/' + path
	if (path not in apis) or size == 0:
		abort(404)
	if ((path != '/api/v1/_health') and (path != '/api/v1/_crash')):
		if (tot_reqs == 0):
			sem.release()
		tot_reqs += 1
	port = getnexxt()
	if request.method == "POST":	
		ret = requests.post(ip+str(port)+path)
	elif request.method == "GET":
		ret = requests.get(ip+str(port)+path)
	else:
		ret = requests.delete(ip+str(port)+path)
	return jsonify(ret.text), ret.status_code

@app.route("/api/v1/acts/upvote",methods=['POST'])
def upvote():
	port=getnexxt()
	data1=request.data
	print(port)
	ret = requests.post(ip+str(port)+'/api/v1/acts/upvote',data1)
	return ret.text, ret.status_code

@app.route("/api/v1/categories",methods=['GET','POST'])
def categories():
	port=getnexxt()
	if(request.method=='GET'):
		ret = requests.get(ip+str(port)+'/api/v1/categories')
		if(ret.status_code==200):
			return jsonify(ret.json()), ret.status_code
		else:
			return ret.text, ret.status_code
	else:
		data1=request.data
		ret = requests.post(ip+str(port)+'/api/v1/categories',data1)
		return ret.text, ret.status_code

@app.route("/api/v1/categories/<categoryName1>",methods=['DELETE'])
def deletecategory(categoryName1):
	port=getnexxt()
	ret = requests.delete(ip+str(port)+'/api/v1/categories/'+categoryName1)
	return ret.text, ret.status_code

@app.route("/api/v1/categories/<categoryName>/acts",methods=['GET'])
def listacts(categoryName):
	port=getnexxt()
	st=request.args.get('start')
	ed=request.args.get('end')
	if(st and ed):
		ret = requests.get(ip+str(port)+'/api/v1/categories/'+categoryName+'/acts?start='+st+"&end="+ed)
		if(ret.status_code==200):
			return jsonify(ret.json()), ret.status_code
		else:
			return ret.text, ret.status_code
	else:
		ret = requests.get(ip+str(port)+'/api/v1/categories/'+categoryName+'/acts')
		if(ret.status_code==200):
			return jsonify(ret.json()), ret.status_code
		else:
			return ret.text, ret.status_code

@app.route("/api/v1/acts",methods=['GET','POST'])
def upload():
	port=getnexxt()
	k=request.get_json(force=True)
	print(k)
	ret = requests.post(ip+str(port)+'/api/v1/acts',data=json.dumps(k))
	return ret.text, ret.status_code

@app.route("/api/v1/categories/<categoryName>/acts/size",methods=['GET'])
def sizeacts(categoryName):
	port=getnexxt()
	ret = requests.get(ip+str(port)+'/api/v1/categories/'+categoryName+'/acts/size')
	return ret.text, ret.status_code

@app.route("/api/v1/acts/<actid>",methods=['DELETE'])
def remove(actid):
	port=getnexxt()
	ret=requests.delete(ip+str(port)+'/api/v1/acts/'+actid)
	return ret.text, ret.status_code

def lock_sem():
	global sem, app
	sem.acquire()
	app.run(host='0.0.0.0', port=80)

def healthcheck():
	global containers, ip
	while True:
		time.sleep(10)
		for c, cont in enumerate(containers):
			if requests.get(ip+str(cont['port'])+"/api/v1/_health").status_code != 200:
				stopcontainer(c)
				startnewcontainer(cont['port'], c)

def autoscale():
	global tot_reqs, size, sem
	sem.acquire()
	while True:
		time.sleep(120)
		if tot_reqs < 20:
			while size > 1:
				stopcontainer(size-1)
			while size < 1:
				startnewcontainer(size+8000, size)
		elif tot_reqs < 40:
			while size > 2:
				stopcontainer(size-1)
			while size < 2:
				startnewcontainer(size+8000, size)
		elif tot_reqs < 60:
			while size > 3:
				stopcontainer(size-1)
			while size < 3:
				startnewcontainer(size+8000, size)	
		else:
			while size > 4:
				stopcontainer(size-1)
			while size < 4:
				startnewcontainer(size+8000, size)

		tot_reqs = 0
	sem.release()

def handler(sig, frame):
	delete()
	sys.exit(0)

if  __name__ == "__main__":
	signal.signal(signal.SIGINT, handler)
	print('press CTRL+C to exit')
	startnewcontainer(8000, 0)
	thread1 = threading.Thread(target = fun1)
	thread2 = threading.Thread(target = fun2)
	thread3 = threading.Thread(target = fun3)
	thread1.start()
	thread2.start()
	thread3.start()