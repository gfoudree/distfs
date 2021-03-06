import logging
import asyncio
import sys

from kademlia.network import Server
from kademlia.routing import RoutingTable

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)

loop = asyncio.get_event_loop()
loop.set_debug(True)

server = Server()
server.listen(8469)
bootstrap_node = ('127.0.0.1', 8468)
loop.run_until_complete(server.bootstrap([bootstrap_node]))

#loop.run_until_complete(server.set("key", "a"*1024*4))

print(server.bootstrappableNeighbors())

result = loop.run_until_complete(server.get('key'))
server.stop()
loop.close()

print("Get result:", result)