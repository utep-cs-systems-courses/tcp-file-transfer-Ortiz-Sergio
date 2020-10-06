#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os

sys.path.append("../lib")       # for params
import params
from os.path import exists

from framedSock import framedSend, framedReceive


switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

addrFamily = socket.AF_INET
socktype = socket.SOCK_STREAM
addrPort = (serverHost, serverPort)

s = socket.socket(addrFamily, socktype)

if s is None:
    print('could not open socket')
    sys.exit(1)

s.connect(addrPort)

print("Welcome to the file transfer program!")
print("Enter the file to send, or -1 to exit")
user_file = input("$ ")

while True:
    if user_file == "-1":
        print("Thank you for using my program!")
        sys.exit(0)

    while not (exists(user_file)):
        print("File does not exist, try again")
        user_file = input("$ ")
        continue

    file_copy = open(user_file, 'rb')
    file_data = file_copy.read()
    if len(file_data) == 0:
        print("Cannot send empty file, try again")
        user_file = input("$ ")
        continue
    else:
        print("What do you want to name the output file?")
        new_file = input("$ ")
        framedSend(s, new_file.encode(), debug)
        file_exists = framedReceive(s, debug)
        file_exists = file_exists.decode()
        if file_exists == 'True':
            print("File already exists in the server, try again")
            user_file = input("$ ")
            continue
        else:
            try:
                framedSend(s, file_data, debug)
            except:
                print("connection lost while sending, exiting")
                sys.exit(0)
            try:
                framedReceive(s, debug)
            except:
                print("connection lost while receiving, exiting")
                sys.exit(0)

    print("Enter the file to send, or -1 to exit")
    user_file =  input("$ ")
    
      
