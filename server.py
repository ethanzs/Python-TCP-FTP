# FTP TCP SERVER IMPLEMENTATION - server.py
# Ethan Seligman

import socket
import os
import sys

# CONFIG
HOST = "localhost"
C_PORT = sys.argv[1]
D_PORT = sys.argv[2]
CHUNK_SIZE = 1024
HEADER_SIZE = 10

# control socket - TCP
sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
sc.bind((str(HOST), int(C_PORT)))
sc.listen(5)
# data socket - TCP
sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sd.bind((str(HOST), int(D_PORT)))
sd.listen(5)

# send data with a padding of 10 bytes with an integer (length of message being sent) aligned left
def send_data(client, msg):
    msg = str(msg)
    msg = "{:10}".format(len(msg)) + msg
    client.send(bytes(msg, "utf-8"))

# get header size which is an integer with a padding of 10 bytes and aligned left. specifies the exact length in bytes of the successor data being received
def getHeaderSize(client):
    # header is 10 bytes
    header = client.recv(HEADER_SIZE).decode("utf-8", "ignore")
    return int(header[:HEADER_SIZE])

# receive exact bytes from client in bytes
def receive(client):
    msg = client.recv(getHeaderSize(client))
    return msg

# receive exact bytes from client in UTF-8 format
def receiveUTF(client):
    msg = client.recv(getHeaderSize(client))
    return msg.decode("utf-8")

# ls command function - list all files in current working directory set by cd command
def ftp_ls(client):  # list all files in current working directory
    dir = ""
    for x in os.listdir('.'):
        if(os.path.isdir(x)):
            dir += "[" + x + "] "
        else:
            dir += x + " "
    if(dir == ""):
        ack = "null"
        send_data(client, ack)
    else:
        ack = "{dir}".format(dir=dir)
        send_data(client, ack)

# cd command function - change directory
def ftp_cd(command):  # change working directory for server
    cd = command[3:]
    try:
        os.chdir(cwd+"/"+cd)
        ack = "{cwd}".format(cwd=os.getcwd())
        send_data(clientsocket_c, ack)
    except FileNotFoundError as e:
        ack = "No such directory. {e}".format(e=e)
        send_data(clientsocket_c, ack)

# get command function - get file from server in current working directory set by cd command
def ftp_get(command):  # send file to client
    if(len(command) != 3):
        fileName = command[4:]
        try:
            f = open(fileName, 'rb')
            ack = "Downloading {fileName}...".format(fileName=fileName)
            send_data(clientsocket_c, ack)
            fileSize = os.path.getsize(fileName)
            sizeSent = 0
            # print(f"FILESIZE = {fileSize}")
            send_data(clientsocket_c, fileSize)
            while fileSize != sizeSent:
                chunk = f.read(CHUNK_SIZE)
                clientsocket_d.send(chunk)
                sizeSent += len(chunk)
            f.close()
            # send success message to client
            send_data(clientsocket_c, "Success")
        except FileNotFoundError:
            ack = "'{fileName}' was not found or is not a valid target.".format(
                fileName=fileName)
            send_data(clientsocket_c, ack)
    else:
        ack = "Invalid syntax. Use: get <filename>"
        send_data(clientsocket_c, ack)

# put command function - upload file from client to server with a specified directory
def ftp_put(command):  # download a file from client
    ack = command
    send_data(clientsocket_c, ack)
    ack = receiveUTF(clientsocket_c)
    if(ack[0] == 'D'): # if file was found
        fileNameFull = command[4:] # grab full file name with directory
        index = fileNameFull.rfind("/") # reverse search until first '/' is found to get file name index range
        fileName = fileNameFull[index+1:] # use reverse search index to assign fileName variable
        # overwrite any files already there
        f = open(fileName, "w")
        f.write("")
        f.close()
        fullData = bytes()
        # receive fileSize
        fileSize = int(receiveUTF(clientsocket_c))
        sizeReceived = 0
        # print(f"FILESIZE={fileSize}")
        while sizeReceived != fileSize: # receive data until size received matches fileSize
            data = clientsocket_d.recv(CHUNK_SIZE)
            fullData += data
            sizeReceived += len(data)
            print("Downloading... {percent}% - {numerator}KB/{denominator}KB".format(percent=int((sizeReceived/fileSize)*100), numerator=sizeReceived/1000, denominator=fileSize/1000, fileSize=fileSize))
        # print(f"DATA RECV'd = {fullData}")
        f = open(fileName, "wb")
        f.write(fullData) # write total data received in binary to file
        f.close()
        send_data(clientsocket_d, "success") # send success message to client
        print("'{fileName}' was successfully downloaded.".format(
            fileName=fileName))
    else:
        print(ack)

print("Waiting for connection...")

while True:
    # accept connections
    clientsocket_c, address_c = sc.accept()
    clientsocket_d, address_d = sd.accept()
    print("Connection from '{address_c}' has been established on port {C_PORT}.".format(address_c=address_c, C_PORT=C_PORT))
    print("Connection from '{address_d}' has been established on port {D_PORT}".format(address_d=address_d, D_PORT=D_PORT))
    # send acknowledgement for connection established
    send_data(clientsocket_c,
              "Successful connection to control socket {port}.".format(port=C_PORT))
    send_data(clientsocket_d,
              "Successful connection to data socket {port}.".format(port=D_PORT))
    command = ""
    while command != "exit":
        # receive command
        # REPLACE WITH FUNCTION THAT GETS COMMAND FROM DIFFERENT PORT!!!!!!!!!!!
        command = receiveUTF(clientsocket_c)
        print("{address_c[0]}: {command}".format(
            address_c=address_c, command=command))
        ack = ""
        cwd = os.getcwd()
        # decode command
        if(command == "ls"):  # if command from client is 'ls'
            ftp_ls(clientsocket_c)
        # if command from client is 'cd'~
        elif(command[0:2] == "cd"):
            ftp_cd(command)
        elif(command[0:3] == "get"):  # if command from client is 'get'
            ftp_get(command)
        elif(command[0:3] == "put"):  # if command from client is 'put'
            ftp_put(command)
        elif(command == "exit"):  # if command from client is 'exit'
            ack = "Terminating connection on port {C_PORT}...".format(C_PORT=C_PORT)
            ack2 = "Terminating connection on port {D_PORT}...".format(C_PORT=C_PORT)
            send_data(clientsocket_c, ack)
            send_data(clientsocket_d, ack2)
            clientsocket_d.close()
            clientsocket_c.close()
        else:
            ack = "'{command}' not recognized as a command.".format(command=command)
            send_data(clientsocket_c, ack)
    # print out that client has terminated connection
    print("{address_c[0]} has terminated its connection on port {C_PORT}.".format(
        address_c=address_c, C_PORT=C_PORT))
    print("{address_d[0]} has terminated its connection on port {D_PORT}".format(
        address_d=address_d, D_PORT=D_PORT))
