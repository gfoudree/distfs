#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 07:53:54 2018

@author: gfoudree
"""

import time
import socket
import threading

def start_server():
    host = 'localhost'
    port = 9528
    running = True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   
    s.bind((host, port))
    s.listen(10)
    
    while running:
        conn, addr = s.accept()
        print("Connection from " + str(addr))
        while 1:
            data = conn.recv(4096)
            if not data:
                break
            print(data)
            
        conn.close()
    s.close()

thread = threading.Thread(target=start_server)
thread.start()


thread.join()