import logging
import asyncio

from kademlia.network import Server

def launch_bootstrap():
    
    server = Server()
    server.listen(8468)
    
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
    loop.close()