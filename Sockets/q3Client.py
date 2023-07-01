# This is the client program that uses UDP

# Sequence:
#
# 1. Create a socket
# 2. Send messages to it
# (We need to know the server's hostname and port.)

import socket
import time, random
n=10
# create a socket
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# The first argument should be AF_INET
	# The second argument is SOCK_STREAM for TCP service
	#    and SOCK_DGRAM for UDP service

host='10.196.13.17' 
port=43387  # this is the server's port number, which the client needs to know

# send some bytes (encode the string into Bytes first)
""" message = "I could tell you a UDP joke but I'm not sure you'll get it."
s.sendto( message.encode('utf-8'), (host,port)) """
 
 
for i in range(0,n):
			f=random.uniform(0,1) # This line generates a random floating-point number between 0 and 1, and assigns it to the variable f
			# This code block sets the value of the request variable based on the value of f.
			if f<0.5:
				request = "SEND_TIME" # If f is less than 0.5, the request is set to "SEND_TIME"
			else:
				request = "SEND_DATE" #  Otherwise, it is set to "SEND_DATE"
			s.sendto(request.encode('utf-8'), (host,port))  # This line sends the encoded request to the specified host and port using the sendto method of the s socket.
			data, addr = s.recvfrom(1024) # buffer size is 1024 bytes
			print("Client received MESSAGE=",data.decode()," from ADDR=",addr)
			time.sleep(random.uniform(1,2)) # This line pauses the execution of the program for a random duration between 1 and 2 seconds using the time.sleep function.
		
 
 


# close the connection
s.close()
