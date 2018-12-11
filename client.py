#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

from main import IPFSNode

def printUsage():
    print("Usage: client <bootstrap IP> <file hash>")
    print()
    print("Retrieves a file from the IPFS network. "
          "Provide a bootstap node as an entry point to the network. "
          "Provide the SHA-512 hash of the file to retrieve.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        printUsage()
        exit(1)

    # Parse arguments
    bootstrapHost = sys.argv[1]
    fileHash = sys.argv[2]
    print("Bootstrap node: {}".format(bootstrapHost))
    print("Getting file with hash: {}".format(fileHash))

    ipfsNode = IPFSNode(bootstrapHost)
    (retrievedFile, metadata) = ipfsNode.getFile(fileHash)
    print("Saving downloaded file to {}.download".format(metadata['fileName']))
    
    # Save file
    with open(metadata['fileName'] + '.download', 'wb') as f:
        f.write(retrievedFile)
    os._exit(0)