# This is the client program

# Sequence:
#
# 1. Create a socket
# 2. Connect it to the server process. 
#	We need to know the server's hostname and port.
# 3. Send and receive data 

import socket

# create a socket
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# The first argument AF_INET specifies the addressing family (IP addresses)
	# The second argument is SOCK_STREAM for TCP service
	#    and SOCK_DGRAM for UDP service


# connect to the server
host='10.196.13.17'
port=43389  # this is the server's port number, which the client needs to know
s.connect((host,port))

# send some bytes
s.send("Pranav".encode('utf-8'))
# read a response
response = s.recv(1024)
print("CLIENT RECEIVED: ",response.decode())

 

def check_string(input_string):
    sp_val=input_string.split()
    if len(sp_val)!=3:
        return "Invalid string"
    else:
        num1 =sp_val[0]
        operation = sp_val[1]
        num2 = sp_val[2]
        # Check if the first element is a valid number
        try:
            num1 = float(num1)
        except ValueError:
            return "Incorrect input format. First element must be a valid number."
        # Check if the third element is a valid number
        try:
            num2 = float(num2)
        except ValueError:
            return "Incorrect input format. Third element must be a valid number."
        
        # Check if the second element is a valid operation
        if operation not in ["+", "-", "*", "/","**",]:
            return "Incorrect input format. Second element must be a valid operation (+, -, *, /,**)"
 
    return "1"
        

while True:
    val=input("Enter the string:")
    if(val=="q"):
        s.send(val.encode('utf-8'))
        response = s.recv(1024)
        print("CLIENT RECEIVED: ",response.decode())
        # close the connection
        s.close()
        break


    f=check_string(val)
    if(f!="1"):
           print(f)
    else:
        s.send(val.encode('utf-8'))
		# read a response
        response = s.recv(1024)
        print("CLIENT RECEIVED :",response.decode())
         
    
         
            



 