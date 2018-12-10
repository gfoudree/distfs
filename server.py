#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from main import IPFSNode
from dht_bootstrap_node import launch_bootstrap

def printUsage():
    print("Usage: server [<bootstrapHost> [<file>]]")
    print()
    print("Starts a node on the IPFS network. "
          "If the optional bootstrap node is provided, it will connect to an "
          "existing IPFS network.")

if __name__ == '__main__':
    if len(sys.argv) > 3:
        printUsage()
        exit(1)
    
    # Parse arguments
    if len(sys.argv) >= 2:
        bootstrapHost = sys.argv[1]
        print("Bootstrap node: {}".format(bootstrapHost))
        if len(sys.argv) == 3:
            fileName = sys.argv[2]
        else:
            fileName = None
    else:
        print("Launching bootstrap node")
        launch_bootstrap()
        exit(0)

    print("Connecting to existing IPFS network")
    ipfsNode = IPFSNode(bootstrapHost)

    if fileName != None:
        print("Adding file to IPFS network")
        ipfsNode.addFile(fileName, False)