import logging
import asyncio

from kademlia.network import Server

def launch_bootstrap(listenPort: int = 8468):
    
    server = Server()
    server.listen(listenPort)
    
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
    loop.close()