# FTP TCP CLIENT IMPLEMENTATION - client.py
# Ethan Seligman

import socket
import os
import sys

# CONFIG
HOST = sys.argv[1]
C_PORT = sys.argv[2]
D_PORT = sys.argv[3]
CHUNK_SIZE = 1024
HEADER_SIZE = 10

# control socket
sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to server with HOST=ip, PORT=port
sc.connect((str(HOST), int(C_PORT)))
# data socket
sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to server with HOST=ip, PORT=port
sd.connect((str(HOST), int(D_PORT)))

# send data with a padding of 10 bytes with an integer (length of message being sent) aligned left
def send_data(s, msg):
    msg = str(msg)
    msg = "{:10}".format(len(msg)) + msg
    s.send(bytes(msg, "utf-8"))


# get header size which is an integer with a padding of 10 bytes and aligned left. specifies the exact length in bytes of the successor data being received
def getHeaderSize(s):
    # header is 10 bytes
    header = s.recv(HEADER_SIZE).decode("utf-8", "ignore")
    return int(header[:HEADER_SIZE])


# receive exact bytes from client in bytes
def receive(s):
    msg = s.recv(getHeaderSize(s))
    return msg


# receive exact bytes from client in UTF-8 format
def receiveUTF(s):
    msg = s.recv(getHeaderSize(s))
    return msg.decode("utf-8")


# ls command function - list all files in current working directory set by cd command
def ftp_get(command):
    if ack[0] == "D":  # if file is found on server side
        fileName = command[4:]
        # explode directory
        # overwrite any files already there
        f = open(fileName, "w")
        f.write("")
        f.close()
        fullData = bytes()
        # receive fileSize
        fileSize = int(receiveUTF(sc))
        sizeReceived = 0
        while sizeReceived != fileSize:
            data = sd.recv(CHUNK_SIZE)
            fullData += data
            sizeReceived += len(data)
            print(
                "Downloading... {percent}% - {numerator}KB/{denominator}KB".format(
                    percent=int((sizeReceived / fileSize) * 100),
                    numerator=sizeReceived / 1000,
                    denominator=fileSize / 1000,
                    fileSize=fileSize,
                )
            )
        f = open(fileName, "wb")
        f.write(fullData)
        f.close()
        receiveUTF(sc)  # wait for data to be done being sent and
        print("'{fileName}' successfully downloaded.".format(fileName=fileName))
    else:
        print(ack)


# put command function - upload file from client to server with a specified directory
def ftp_put(command):
    if len(command) != 3:
        fileNameFull = command[4:]  # grab full file name with directory
        index = fileNameFull.rfind(
            "/"
        )  # reverse search until first '/' is found to get file name index range
        fileName = fileNameFull[
            index + 1 :
        ]  # use reverse search index to assign fileName variable
        directory = fileNameFull[
            : index + 1
        ]  # use reverse search index to assign fileName directory
        found = False
        try:
            for x in os.listdir(directory):
                if x == fileName and not os.path.isdir(x):
                    found = True
        except FileNotFoundError as e:
            found = False
        if found:  # if file was found in directory specified
            ack = "Downloading {fileName}...".format(fileName=fileName)
            send_data(sc, ack)
            f = open(fileNameFull, "rb")
            fileSize = os.path.getsize(fileNameFull)
            sizeSent = 0
            send_data(sc, fileSize)
            while fileSize != sizeSent:
                chunk = f.read(CHUNK_SIZE)
                sd.send(chunk)
                sizeSent += len(chunk)
            f.close()
            receiveUTF(sd)  # receive finish message from server
            print("'{fileName}' was successfully uploaded.".format(fileName=fileName))
        else:
            send_data(sc, "Not found")
            print(
                "File '{fileName}' was not found in this directory.".format(
                    fileName=fileName
                )
            )
    else:
        print("Invalid syntax. Use: put <filename>")


# Get connection acknowledgement from server
print(receiveUTF(sc))
print(receiveUTF(sd))

command = ""
while True:
    # take command in as input
    command = input(">")
    # send command to server
    send_data(sc, command)
    # receive acknowledgement from server regarding command
    ack = receiveUTF(sc)
    if command[:3] == "get":  # if command is get
        ftp_get(command)
    elif command[:3] == "put":  # if command is put
        ftp_put(command)
    elif command[:4] == "exit":  # if command is exit
        ack2 = receiveUTF(sd)
        print(ack)
        print(ack2)
        break
    else:
        print(ack)
sc.close()
sd.close()
print("All connections terminated.")
