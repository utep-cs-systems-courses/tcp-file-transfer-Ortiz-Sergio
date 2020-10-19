#! /usr/bin/env python3

import sys, os, threading, time
from threading import Thread

sys.path.append("../../lib")       # for params
import re, socket, params
from os.path import exists
from encapFramedSock import EncapFramedSock

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

lock = threading.Lock()

class Server(Thread):
    def __init__(self, sockAddr):
        Thread.__init__(self)
        self.sock, self.addr = sockAddr
        self.fsock = EncapFramedSock(sockAddr)

    def run(self):
        print("new thread handling connection from", self.addr)
        while True:
            payload = self.fsock.receive(debug)
            if debug: print("rec'd: ", payload)
            
            if not payload: #connection done
                if debug: print(f"thread connected to %s  done" % self.addr)
                self.fsock.close()
                return
            
            payload = payload.decode()

            lock.acquire()
            if debug:
                time.sleep(5)
            
            if exists(payload):
                self.fsock.send(b"True", debug)
            else:
                self.fsock.send(b"False", debug)
                try:
                    payload2 = self.fsock.receive(debug)
                except:
                    print("connection lost while receiving")
                    sys.exit(0)

                if not payload2:
                    break
                
                payload2 += b"!"
                
                try:
                    self.fsock.send(payload2, debug)
                except:
                    print("connection lost while sending")

                output = open(payload, 'wb')
                output.write(payload2)
                output.close()
                self.fsock.close()
                lock.release()
            
def main():
    while True:
        sock_addr = lsock.accept()
        server = Server(sock_addr)
        server.start()

if __name__ == "__main__":
    main()
