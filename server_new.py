import socket
import os
import thread
import sys
import mimetypes
import datetime
import requests
from mimetools import Message
counter = {}


exist = 1
if not os.path.isdir(os.getcwd() + "/www/"):
	exist = 0
else:
	directory = os.getcwd() + "/www/"
	os.chdir(directory)

if exist == 0:
	print "Directory www does not exist."
	sys.exit(0)

PORT_NUM = 47906

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
        server_socket.bind(('',PORT_NUM))
except socket.error, msg:
        print "Port " + str(PORT_NUM) + " is already in use.!"
        sys.exit(0)
server_socket.listen(5)
print socket.gethostname() + " serving at port " + str(PORT_NUM)

def get_content_type(rqfile):
	mimetype,fileEncoding = mimetypes.guess_type(rqfile)
	return mimetype

def get_current_time():
	return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

def get_last_mod(rqfile):
	return datetime.datetime.utcfromtimestamp(os.path.getmtime(rqfile)).strftime('%a, %d %b %Y %H:%M:%S GMT')


def Access_counter(counter, requestfile,address):
	current_count = 0
	if(requestfile not in counter):
		counter[requestfile] = 1
		current_count = 1
	else:
		current_count = counter.get(requestfile)
		current_count += 1
		counter[requestfile] = current_count

	str2 = "|"
	for x in address:
		str2 += ''.join(str(x))
		if len(str2) > 3:
			str2 += "|"
	accesslog = requestfile + str2 + str(current_count)
	print(accesslog)

def response(connection,address):
	request = connection.recv(1024)

	if not request:
		requestfile = "sample.html"

	else:
		arr = request.split()
		requestfile = arr[1][1:].strip()
        #requestfile = requestfile[1:].strip()
	filename = os.getcwd() + "/" + requestfile
	if not os.path.isfile(filename) :
		requestfile = ""
		connection.send("""HTTP/1.1 404 NOT FOUND""")
		connection.close()
	else:
		thread.start_new_thread(Access_counter, (counter,requestfile,address))

		fd = open(requestfile)
		file_content = fd.read()
		fd.close()


		content_type = get_content_type(requestfile) # get mime type of requested file
		if(content_type == None):
			content_type = "None"
		current_date = get_current_time() # get current date and time
		mod_time = get_last_mod(requestfile)
        	responsecontent = "HTTP/1.1 200 OK  \nDate:" + current_date + " \nServer:MyServer \nLast-Modified:" + mod_time + " \nContent-Type:" + content_type + " \nContent-Length:" + str(os.path.getsize(requestfile)) + "\r\n\n"
		for i in range(0, len(file_content)):
			responsecontent = responsecontent + file_content[i]
		connection.send(responsecontent)
		connection.close()

####### Multithreading #########
while True:
	connection, address = server_socket.accept()
	thread.start_new_thread(response,(connection, address))
