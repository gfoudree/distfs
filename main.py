#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  8 15:14:20 2018

@author: gfoudree
"""
import hashlib

block_size = 1024*16 #16k block size

def chunkFile(data: str):
    chunks = []
    for i in range(0, len(data), block_size):
        chunk = data[i:i + block_size]
        hsh = hashlib.sha512(chunk).hexdigest()
        chunks.append({"data" : chunk, "hash" : hsh, "len" :len(chunk)})
    return chunks
    
def addFile(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
        
        