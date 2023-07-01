# importing all libraries
import threading
import socket
import datetime

# function to broadcast messages to all connected clients
def broadcast(msg):
    for c_socket in clients:
        c_socket.send(msg.encode('utf-8'))

# function to handle communication with a specific client 
def chat(client):
    while(True):
        try:
             # getting the index of the current client and their nickname
            ind = clients.index(client)
            nickname = nicknames[ind]
            
            # receive messages from the client
            message = client.recv(1024).decode()
           
            # check if the client is sending the quit command
            if message == f'{nickname}: /quit':
                
                # remove the client from the clients and nicknames lists
                clients.remove(client)
                nicknames.remove(nickname)
                
                # close the socket and broadcast the disconnection message
                client.close()
                broadcast(f'{nickname} disconnected')
                print(f'{nickname} disconnected')
                break

            # if the client is not sending the quit command, broadcast the message    
            else:
                broadcast(message)
        except:
            # if an error occurs, remove the client from the clients and nicknames lists, close the socket and broadcast the disconnection message
            ind = clients.index(client)
            clients.remove(client)
            nickname = nicknames[ind]
            nicknames.remove(nickname)
            
            client.close()
            broadcast(f'{nickname} disconnected')
            print(f'{nickname} disconnected')
            break

# function to handle incoming connections
def receive():
    while(True):
        
        # accept incoming connections        
        client, addr = s.accept()
        print("Connection initiated from ",addr)

        # send the nickname prompt to the client        
        client.send("nickname".encode('utf-8'))
        data = client.recv(1024)

        # receive the client's nickname        
        nickname = data.decode()
        
        # add the client to the clients        
        clients.append(client)
        
        # add the nickname to the clients
        nicknames.append(nickname)
        
        # saving the datetime
        now = datetime.datetime.now()
        
        # printing connection status
        print(f'{nickname} connected')
        broadcast(f'{nickname} connected')
        client.send('Welcome to the chatroom!'.encode('utf-8'))
        broadcast(f'It is {str(now)}\n Member count:{len(clients)}')
        
        #thread to multi task 
        thread = threading.Thread(target=chat, args=(client,))
        thread.start()
        
# print server started 
print("Server started...waiting for a connection from the client")

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the server
host='10.196.13.17'
port=43389  # this is the server's port number, which the client needs to know
s.bind((host,port)) 
s.listen()

clients = []
nicknames = []
receive()   