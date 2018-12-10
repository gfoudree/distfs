#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from main import IPFSNode

def printUsage():
    print("Usage: client <listen port> <bootstrap IP> <bootstrap port> <file hash>")
    print()
    print("Retrieves a file from the IPFS network. "
          "Provide a bootstap node as an entry point to the network. "
          "Provide the SHA-512 hash of the file to retrieve.")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        printUsage()
        exit(1)
    
    # Parse arguments
    listenPort = int(sys.argv[1])
    bootstrapHost = sys.argv[2]
    bootstrapPort = int(sys.argv[3])
    fileHash = sys.argv[4]
    print("Listen on port: {}".format(listenPort))
    print("Bootstrap node: {}:{}".format(bootstrapHost, bootstrapPort))
    print("Getting file with hash: {}".format(fileHash))

    ipfsNode = IPFSNode(listenPort, bootstrapHost, bootstrapPort)
    retrievedFile = ipfsNode.getFile(fileHash)