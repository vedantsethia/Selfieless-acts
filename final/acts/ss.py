@app.route("/api/v1/_health",methods=['GET'])
def sizeacts1111():
	global health
	if(health==1):
		return make_response(jsonify({ }),200)
	else:
		return make_response(jsonify({ }),500)

########################################################################################################
@app.route("/api/v1/_crash",methods=['POST'])
def sizeacts1111():
	global health
	if(health==0):
		return make_response(jsonify({ }),500)
	else:
		health=0
		return methodsake_response(jsonify({ }),200)

global health
	if(health==0):
		return make_response(jsonify({ }),500)