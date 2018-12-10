#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 15:14:20 2018

@author: gfoudree
"""
import hashlib
import os
import logging
import asyncio
import sys
import time
import socket

from kademlia.network import Server
from kademlia.routing import RoutingTable

from dht_bootstrap_node import *

block_size = 1024*4 #16k block size
debug = True

class Blob():
    def __init__(self):
        self.data = ''
        
    def setData(self, data: str):
        self.data = data
        
    def getData(self) -> str:
        return self.data
    
class List():
    def __init__(self, fileHash: str, fileName: str, fileLen: int):
        self.links = []
        self.fileHash = fileHash
        self.fileName = fileName
        self.fileLen = fileLen
        
    def addLink(self, hsh, size):
        self.links.append({"hash" : hsh, "size" : size})
        
    def getData(self) -> str:
        return self.links
        
def chunkFile(data: str):
    chunks = []
    for i in range(0, len(data), block_size):
        chunk = data[i:i + block_size]
        hsh = hashlib.sha512(chunk).hexdigest()
        chunks.append({"data" : chunk, "hash" : hsh, "size" :len(chunk)})
    return chunks
    
def addFile(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
        fileHash = hashlib.sha512(data).hexdigest()
        fileLen = len(data)
        fileChunks = chunkFile(data)
        fileName = os.path.basename(filepath)
        
        ipfsList = List(fileHash, fileName, fileLen)
        ipfsBlobs = []
        
        for chunk in fileChunks:
            ipfsBlob = Blob()
            ipfsBlob.setData(chunk['data'])
            ipfsBlobs.append(ipfsBlob)
            
            ipfsList.addLink(chunk['hash'], chunk['size'])
        
        if debug:
            print(ipfsList.getData())
            print("\n\n\n")
            for blob in ipfsBlobs:
                print(blob.getData())
        
# call addFile()

# Store List() of file chunks

if __name__ == '__main__':
    print("running")
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('kademlia')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    target = os.getenv('TARGET') #Get env from docker
    if target == 'bootstrap':
        launch_bootstrap()
    else:
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        
        server = Server()
        server.listen(8469)
        bootstrap_ip = socket.gethostbyname('bootstrap')
        bootstrap_node = (bootstrap_ip, 8468)
        loop.run_until_complete(server.bootstrap([bootstrap_node]))
        
        print(server.bootstrappableNeighbors())
        loop.run_until_complete(server.set("key", "a"*1024*4))
        time.sleep(1)
        result = loop.run_until_complete(server.get('key'))
        server.stop()
        loop.close()

        print("Get result:", result)
        #addFile("./LICENSE")