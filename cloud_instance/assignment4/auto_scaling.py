import requests
import time
import os
import subprocess as sp
import ast 
import re,threading
from threading import Timer
i = 1
prev_cnt_req = 0
line = 3
class RepeatTimer(Timer):
	def run(self):
		while not self.finished.wait(self.interval):
			self.function(*self.args,**self.kwargs)


def	timeout():
	print("5 sec")
	global prev_cnt_req
	#total number of requests
	p1 = sp.Popen(["sudo", "cat" ,"/var/log/nginx/access.log"],stdout=sp.PIPE)
	p2 = sp.Popen(["wc", "-l"], stdin = p1.stdout , stdout=sp.PIPE)

	p3 = p2.communicate()[0].decode("utf-8").split("\n")
	cnt_request = int(p3[0])
	
	#total no of active containers
	q1 = sp.Popen(["sudo", "docker" ,"ps"],stdout=sp.PIPE)
	q2 = sp.Popen(["grep", "acts"], stdin = q1.stdout , stdout=sp.PIPE)
	q3 = sp.Popen(["wc", "-l"], stdin = q2.stdout , stdout=sp.PIPE)
	q4 = q3.communicate()[0].decode("utf-8").split("\n")
	cnt_active_cont = int(q4[0])
	cont = sp.Popen(["sudo", "docker" ,"ps"],stdout=sp.PIPE)
	
	if (int((cnt_request - prev_cnt_req) /20) + 1) < cnt_active_cont:  #scale down (cnt_request/20) + 1
			
			y=cont.communicate()[0].decode("utf-8").split("\n")
			
			diff = cnt_active_cont - int((cnt_request - prev_cnt_req )/20) - 1 
			
			for m in range(8000 + cnt_active_cont - 1,8000 + cnt_active_cont - int(diff) - 1, -1):
				
				for t in range(1,len(y)-1):
				
					
					port = re.search(":[0-9][0-9][0-9][0-9]",y[t])
					
					if(int(port.group(0)[1:]) == m):
						os.system("sudo docker stop {}".format(y[t][0:12]))
						os.system("sudo docker rm {}".format(y[t][0:12]))
						os.system("sudo sh -c \"sed -i '/{}/d' /etc/nginx/conf.d/nginx1.conf\"".format(l))
			
	elif (int((cnt_request - prev_cnt_req )/20) + 1) > cnt_active_cont: #scale up (cnt_request/20) + 1
			
			diff = int((cnt_request - prev_cnt_req )/20) + 1 - cnt_active_cont
			
			for l in range(8000 + cnt_active_cont,8000 + int(diff) + cnt_active_cont):
				os.system("sudo docker run -d -p {}:80 -v /home/ubuntu/database1:/data acts".format(l))
				os.system("sudo sh -c  \"sed -i '{}server localhost:{} weight=1;' /etc/nginx/conf.d/nginx1.conf\" ".format(line,l))
				line = line + 1
				time.sleep(1)
			os.system("sudo systemctl restart nginx")
			
	prev_cnt_req = cnt_request
	


timer = RepeatTimer(120.0,timeout)
while(True):
	
	p1 = sp.Popen(["sudo", "cat" ,"/var/log/nginx/access.log"],stdout=sp.PIPE)
	p2 = sp.Popen(["wc", "-l"], stdin = p1.stdout , stdout=sp.PIPE)

	p3 = p2.communicate()[0].decode("utf-8").split("\n")
	cnt_request = int(p3[0])
	

	
	if cnt_request == 1 and i==1:   #if cnt_request doesnot increase then we dont need to again start the timer
		timer.start()
		i=0
		


	
		

