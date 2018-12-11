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
import threading

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
    def __init__(self, fileHash: str, fileName: str, fileLen: int, compression: bool):
        self.links = []
        self.fileHash = fileHash
        self.fileName = fileName
        self.fileLen = fileLen
        self.compression = compression
        
    def addLink(self, hsh, size):
        self.links.append({"hash" : hsh, "size" : size})
        
    def getData(self) -> str:
        return self.links
    
    def __str__(self):
        return str({'fileHash' : self.fileHash, 'fileName' : self.fileName, 
                    'fileLen' : self.fileLen, 'links' : self.links, 'compression' : self.compression})
        
class IPFSNode():
    def __init__ (self, bootstrapHost: str = 'bootstrap'):
        self.server = Server()
        self.server.listen(8469)
        self.has_list = []
        
        # Hack to get the "deafult" IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.1.1.1', 80))
        self.local_ip = s.getsockname()[0]
        s.close()

        #self.local_ip = socket.gethostbyname(socket.gethostname())
        bootstrap_ip = socket.gethostbyname(bootstrapHost)
        self.bootstrap_node = (bootstrap_ip, 8469)
        
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        
        self.loop.run_until_complete(self.server.bootstrap([self.bootstrap_node]))
        
        neighbors = self.server.bootstrappableNeighbors()
        
        for node in neighbors:
            print("DHT Peer found! {0}:{1}".format(node[0], node[1]))
            
        print("Starting TCP transfer server")
        self.tcpThread = threading.Thread(target = self.startTCPServer)
        self.tcpThread.start()
        
    def startTCPServer(self):
        host = '0.0.0.0'
        port = 9528
        self.running = True
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       
        s.bind((host, port))
        s.listen(10)
        
        while self.running:
            conn, addr = s.accept()
            print("Connection from " + str(addr))
            sys.stdout.flush()
            while 1:
                data = conn.recv(4096)
                if not data:
                    break
                # Check if data is correct format
                data = data.decode('utf-8')
                if (len(data) == 133 or len(data) == 134) and data[0:5] == 'hash=':
                    requestedHash = data[5:134]
                    print("looking for hash " + requestedHash)
                    sys.stdout.flush()
                    #Find requested hash in our data
                    found = False
                    for has_chunk in self.has_list:
                        if has_chunk[1] in requestedHash:
                            conn.send(has_chunk[0]) #Send the found data
                            found = True
                            break
                    
                    if not found:
                        conn.send(b"notfound")
                else:
                    conn.send(b"invalid_request")
                print("Request: " + data)
                sys.stdout.flush()
                
            conn.close()
        s.close()
        
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
    
    def addFile(self, filepath: str, compression: bool):
        with open(filepath, 'rb') as f:
            data = f.read()
            fileHash = hashlib.sha512(data).hexdigest()
            fileLen = len(data)
            
            if compression: #Compress data if necessary
                data = zlib.compress(data, level = 7)
            
            fileChunks = self.chunkFile(data)
            fileName = os.path.basename(filepath)
            
            ipfsList = List(fileHash, fileName, fileLen, compression)
            ipfsBlobs = []
            
            for chunk in fileChunks:
                ipfsBlob = Blob()
                ipfsBlob.setData(chunk['data'], chunk['hash'])
                ipfsBlobs.append(ipfsBlob)
                
                ipfsList.addLink(chunk['hash'], chunk['size'])
                
                #Add data to our has list
                self.has_list.append((chunk['data'], chunk['hash']))
            
            print(ipfsList)
            if debug:
                print(ipfsList.getData())
                print("\n\n\n")
                for blob in ipfsBlobs:
                    print(blob.getData())
            if self.server:
                #Need to add data onto DHT network
                
                self.setDHTKey(fileHash, str(ipfsList)) #Add master file record to DHT
                
                for blob in ipfsBlobs: #Add items onto DHT
                    block = blob.getData()
                    if len(block['data']) > 1024: #If the block is bigger than 1k, add to local TCP server
                        self.setDHTKey(block['hash'], 'ip=' + self.local_ip)
                    else: #Otherwise store directly on DHT
                        self.setDHTKey(blob.getData()['hash'], blob.getData()['data'])
                
                return fileHash
            
    def TCPGet(self, host, hsh):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 9528))
        if not isinstance(hsh, bytes):
            hsh = hsh.encode()
            
        s.send(b'hash=' + hsh + b'\n')
        data = s.recv(8192)
        s.close()
        
        return data
    
    def getFile(self, hsh: str) -> (bytes, dict):
        masterFileRecord = self.getDHTKey(hsh) #Get metadata
        metadata = None
        
        #Convert from string dictionary to python dictionary
        if masterFileRecord and len(masterFileRecord) > 1:
            masterFileRecord = masterFileRecord.replace("'", "\"").replace('True', 'true').replace('False', 'false') #transform into valid JSON
            metadata = json.loads(masterFileRecord)
        else:
            raise Exception("Unable to locate file record on network!")
            
        fileContents = b''
        for link in metadata['links']:
            DHTData = self.getDHTKey(link['hash'])
            data = None
            if not DHTData:
                raise Exception("Unable to get part of file with hash " + link['hash'])
                
            if DHTData[0:3] == 'ip=': #Need to get data via TCP not DHT
                data = self.TCPGet(DHTData[3:], link['hash'])
            else:
                data = DHTData
                
            if len(data) != link['size']:
                raise Exception("Hash value ({}) has invalid or corrupted length".format(link['hash']))
            
            fileContents += data
            
        if metadata['compression']:
            fileContents = zlib.decompress(fileContents)
        return (fileContents, metadata)
    
    def __del__(self):
        self.server.stop()
        self.loop.close()
        self.tcpThread.join()
        
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
       storedHash = ipfsNode.addFile('./LICENSE', False)
       print("{} stored on IPFS".format(storedHash))
       
       (retrievedFile, metadata) = ipfsNode.getFile(storedHash)
       
       print(b"Original file contents recovered:\n" + retrievedFile)