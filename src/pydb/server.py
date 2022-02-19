import websockets
import asyncio
import json
import traceback

import commands
from exceptions import *

class ActiveConnections:
    def __init__(self):
        self.conns = {}
    
    def addConn(self, websocket, loggedIn=False, expires=None):
        if loggedIn and expires is not None:
            data = {
                "loggedIn": True,
                "expires": expires,
            }
        else:
            data = {
                "loggedIn": False,
                "expires": None,
            }
        
        self.conns[websocket.id] = data
    
    def isConn(self, websocket):
        return websocket.id in list(self.conns.keys())
    
    def removeConn(self, websocket):
        del self.conns[websocket.id]
    
    def isLoggedIn(self, websocket):
        self.updateExpired(websocket)
        return self.conns[websocket.id]['loggedIn']
    
    def authoriseConnection(self, websocket):
        self.conns[websocket.id] = {
            "loggedIn": True,
        }
    
    def deauthoriseConnection(self, websocket):
        self.conns[websocket.id] = {
            "loggedIn": False,
        }


activeConnections = ActiveConnections()

def makeResponse(respType, message):
    return json.dumps({
        "response": respType,
        "message": message,
    })


async def keepAlive(websocket):
    """Keep a certain websocket alive

    Args:
        websocket (WebSocketServerProtocol): Websocket in question
    """
    global activeConnections

    while True:
        try:
            test = await websocket.ping()
            await test
        except websockets.exceptions.ConnectionClosed:
            # client disconnected
            activeConnections.removeConn(websocket)
            break

        await asyncio.sleep(15)


async def handle(websocket):
    global activeConnections

    asyncio.create_task(keepAlive(websocket))

    async for msg in websocket:
        try:
            # build a command

            if not activeConnections.isConn(websocket):
                activeConnections.addConn(websocket)

            try:
                cmd = await commands.getCommand(msg)
                await websocket.send(makeResponse(
                    "success",
                    "done"
                ))
            except UnknownCommand:
                await websocket.send(makeResponse(
                    "err",
                    "unknown command"
                ))
            except Exception as e:
                print(traceback.format_exc())
                await websocket.send(
                    json.dumps(makeResponse(
                        "err",
                        f"unexpected error: {str(e)}"
                    ))
                )
        except websockets.exceptions.ConnectionClosed:
            # client disconnected
            activeConnections.removeConn(websocket)


async def main():
    async with websockets.serve(handle, "localhost", 2000):
        # run forever
        await asyncio.Future()


asyncio.run(main())