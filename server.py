#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from main import IPFSNode
from dht_bootstrap_node import launch_bootstrap

def printUsage():
    print("Usage: server <listen port> [<bootstrapHost> <bootstrapPort> [<file>]]")
    print()
    print("Starts a node on the IPFS network. "
          "If the optional bootstrap node is provided, it will connect to an "
          "existing IPFS network.")

if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 4 and len(sys.argv) != 5:
        printUsage()
        exit(1)
    
    # Parse arguments
    listenPort = int(sys.argv[1])
    print("Listen on port: {}".format(listenPort))
    if len(sys.argv) >= 4:
        bootstrapHost = sys.argv[2]
        bootstrapPort = int(sys.argv[3])
        print("Bootstrap node: {}:{}".format(bootstrapHost, bootstrapPort))
        if len(sys.argv) == 5:
            fileName = sys.argv[4]
        else:
            fileName = None
    else:
        print("Launching bootstrap node")
        launch_bootstrap(listenPort)
        exit(0)

    print("Connecting to existing IPFS network")
    ipfsNode = IPFSNode(listenPort, bootstrapHost, bootstrapPort)

    if fileName != None:
        print("Adding file to IPFS network")
        ipfsNode.addFile(fileName, False)