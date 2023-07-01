# This is the client program

# Sequence:
#
# 1. Create a socket
# 2. Connect it to the server process. 
#	We need to know the server's hostname and port.
# 3. Send and receive data 


import socket # include socket
import threading #include threading
nickname= input ("Choose a nicknane: ")
# create a socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# The first argument AF_INET specifies the addressing family (IP addresses)
# The second argument is SOCK_STREAM for TCP service
#    and SOCK_DGRAM for UDP service

# connect to the server
host='10.196.13.17'
port=43389  # this is the server's port number, which the client needs to know
client.connect((host, port))

def receive():
    while(True):
        try:
            message = client.recv(1024).decode()
            if message =="nickname": # If the message is "nickname", it sends the nickname variable encoded in UTF-8 to the client
                client.send(nickname.encode("UTF-8"))
            elif message=="":
                continue  # If the message is an empty string, it continues to the next iteration
            else:
                print(message) #Oit prints the received message
        except:
            print("Disconnected! ") # if message is not received then we are disconnected
            client.close() # close 
            break # break the loop 
# The write function waits for user input
def write():
    while(True):
        val=input()
         # creates a message by concatenating the nickname variable and the input, and sends the message encoded in UTF-8 to the server
        message = f'{nickname}: {val}'
        client.send(message.encode('utf-8'))
        if(val=="/quit"): #  if the user inputs "/quit" and in that case 
            client.close() # closes the client and breaks out of the loop.
            break

# Two threads are created using the threading.Thread function 
# threads are started using the start method       
recievethread = threading.Thread(target = receive) # The receive thread will run the receive function 
recievethread.start()
writethread = threading.Thread(target = write) # the write thread will run the write function
writethread.start()