import requests
import time
import os
import subprocess as sp
import ast 
import re

print("-----------")
#y=cont.communicate()[0].decode("utf-8").split("\n")
#	x=cont.communicate()[1].decode("utf-8")

#print(port.group(0)[1:])
#print(x[132:146])
#print(x[243:247])
#int port_no = 8000

'''cnt = 8000
cont = sp.Popen(["sudo", "docker" ,"ps"],stdout=sp.PIPE)
y=cont.communicate()[0].decode("utf-8").split("\n")
print(len(y))'''


while(True):
		p1 = sp.Popen(["sudo", "docker" ,"ps"],stdout=sp.PIPE)
		p2 = sp.Popen(["grep", "acts"], stdin = p1.stdout , stdout=sp.PIPE)
		p3 = sp.Popen(["wc", "-l"], stdin = p2.stdout , stdout=sp.PIPE)
		p4 = p3.communicate()[0].decode("utf-8").split("\n")
		cnt = int(p4[0])
		print(cnt)
		cont = sp.Popen(["sudo", "docker" ,"ps"],stdout=sp.PIPE)
		s=requests.get("http://localhost:8000/api/v1/_health")
		#print(s.status_code)
		if s.status_code == 500:
			#start_container()
			y=cont.communicate()[0].decode("utf-8").split("\n")
			#print("bye")
			for i in range(1,len(y)):
				#print(type(y[i][111:115]))
				port = re.search(":[0-9][0-9][0-9][0-9]",y[i])
				if(int(port.group(0)[1:]) == 8000):
					os.system("sudo docker stop {}".format(y[i][0:12]))
					os.system("sudo docker rm {}".format(y[i][0:12]))
					#os.system("screen")
					#serial.write('\x20')
					#serial.write('\x01')
					#os.system('c')
					os.system(" sudo docker run -d -p 8000:80 -v /home/ubuntu/database1:/data acts")
					time.sleep(1)
					break
		for i in range(8001,8000 + cnt):			
			try:									
				s=requests.get("http://localhost:{}/api/v1/_health".format(i))
				if s.status_code == 500:
					y=cont.communicate()[0].decode("utf-8").split("\n")
					#print("bye")
					for j in range(1,len(y)):
						#print(type(y[i][111:115]))
						port = re.search(":[0-9][0-9][0-9][0-9]",y[j])
						if(int(port.group(0)[1:]) == i):
							os.system("sudo docker stop {}".format(y[j][0:12]))
							os.system("sudo docker rm {}".format(y[j][0:12]))
							os.system("sudo docker run -d -p {}:80 -v /home/ubuntu/database1:/data acts".format(i))
							time.sleep(1)
							break	
				
		
			except Exception as e:
				msg= "hello"
		time.sleep(1)


