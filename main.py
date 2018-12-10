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
import zlib
import json

from kademlia.network import Server
from kademlia.routing import RoutingTable

from dht_bootstrap_node import *

block_size = 1024*6 #6k block size
debug = True

class Blob():
    def __init__(self):
        self.data = ''
        self.hsh = ''
        
    def setData(self, data: str, hsh: str):
        self.data = data
        self.hsh = hsh
        
    def getData(self) -> dict:
        return {"data": self.data, "hash" : self.hsh}
    
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
    
    def __str__(self):
        return str({'fileHash' : self.fileHash, 'fileName' : self.fileName, 'fileLen' : self.fileLen, 'links' : self.links})
        
class IPFSNode():
    def __init__ (self):
        self.server = Server()
        self.server.listen(8469)
        
        bootstrap_ip = socket.gethostbyname('bootstrap')
        self.bootstrap_node = (bootstrap_ip, 8468)
        
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        
        self.loop.run_until_complete(self.server.bootstrap([self.bootstrap_node]))
        
        neighbors = self.server.bootstrappableNeighbors()
        
        for node in neighbors:
            print("DHT Peer found! {0}:{1}".format(node[0], node[1]))
        
    def chunkFile(self, data: str):
        chunks = []
        for i in range(0, len(data), block_size):
            chunk = data[i:i + block_size]
            hsh = hashlib.sha512(chunk).hexdigest()
            chunks.append({"data" : chunk, "hash" : hsh, "size" :len(chunk)})
        return chunks
        
    def setDHTKey(self, key: str, val: str):
        self.loop.run_until_complete(self.server.set(key, val))
        
    def getDHTKey(self, key: str) -> str:
        return self.loop.run_until_complete(self.server.get(key))
    
    def addFile(self, filepath: str):
        with open(filepath, 'rb') as f:
            data = f.read()
            fileHash = hashlib.sha512(data).hexdigest()
            fileLen = len(data)
            fileChunks = self.chunkFile(data)
            fileName = os.path.basename(filepath)
            
            ipfsList = List(fileHash, fileName, fileLen)
            ipfsBlobs = []
            
            for chunk in fileChunks:
                ipfsBlob = Blob()
                ipfsBlob.setData(chunk['data'], chunk['hash'])
                ipfsBlobs.append(ipfsBlob)
                
                ipfsList.addLink(chunk['hash'], chunk['size'])
            
            print(ipfsList)
            if debug:
                print(ipfsList.getData())
                print("\n\n\n")
                for blob in ipfsBlobs:
                    print(blob.getData())
            if self.server:
                #Need to add data onto DHT network
                
                self.setDHTKey(fileHash, str(ipfsList)) #Add master file record to DHT
                
                for blob in ipfsBlobs:
                    self.setDHTKey(blob.getData()['hash'], blob.getData()['data'])
                
                return fileHash
                    
    def getFile(self, hsh: str):
        masterFileRecord = self.getDHTKey(hsh) #Get metadata
        metadata = None
        
        #Convert from string dictionary to python dictionary
        if masterFileRecord and len(masterFileRecord) > 1:
            masterFileRecord = masterFileRecord.replace("'", "\"") #transform into valid JSON
            metadata = json.loads(masterFileRecord)
        else:
            raise Exception("Unable to locate file record on network!")
            
        fileContents = b''
        for link in metadata['links']:
            data = self.getDHTKey(link['hash'])
            if not data:
                raise Exception("Unable to get part of file with hash " + link['hash'])
            if len(data) != link['size']:
                raise Exception("Hash value ({}) has invalid or corrupted length".format(link['hash']))
            
            fileContents += data
            
        return fileContents
    
    def __del__(self):
        self.server.stop()
        self.loop.close()
        
        

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
       ipfsNode = IPFSNode()
       ipfsNode.setDHTKey('key', 'supersecret')
       #print(ipfsNode.getDHTKey('key'))
       storedHash = ipfsNode.addFile('./LICENSE')
       print("{} stored on IPFS".format(storedHash))
       
       retrievedFile = ipfsNode.getFile(storedHash)
       
       print(b"Original file contents recovered:\n" + retrievedFile)