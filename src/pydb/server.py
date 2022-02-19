import hashlib
import websockets
import asyncio
import json
import traceback

import commands
from exceptions import *
import creds

class ActiveConnections:
    """Management for all active connections
    """
    def __init__(self):
        self.conns = {}
    
    def addConn(self, websocket, loggedIn=False):
        """Add an active connection

        Args:
            websocket (Websocket): The connection
            loggedIn (bool, optional): Whether or not the conn is logged in. Defaults to False.
        """
        data = {
            "loggedIn": loggedIn,
        }
        
        self.conns[websocket.id] = data
    
    def isConn(self, websocket):
        """Determine whether a connection is active"""
        return websocket.id in list(self.conns.keys())
    
    def removeConn(self, websocket):
        """Remove an existing connection"""
        del self.conns[websocket.id]
    
    def isLoggedIn(self, websocket):
        """Determine whether a connection is logged in or not"""
        return self.conns[websocket.id]['loggedIn']
    
    def authoriseConnection(self, websocket):
        """Authorise a certain connection (log them in)"""
        self.conns[websocket.id] = {
            "loggedIn": True,
        }
    
    def deauthoriseConnection(self, websocket):
        """Deauthorise a certain connection (log them out)"""
        self.conns[websocket.id] = {
            "loggedIn": False,
        }


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
            msg = json.loads(msg)
            # build a command

            if not activeConnections.isConn(websocket):
                activeConnections.addConn(websocket)

            # check if authorised
            if not activeConnections.isLoggedIn(websocket):
                await handleAuthorise(websocket, msg)
                continue

            # actual commands
            try:
                await commands.verifyCommand(msg)
                await websocket.send(makeResponse("success", "done"))
            
            except UnknownCommand:
                await websocket.send(makeResponse("err", "unknown command"))
            
            except Exception as e:
                print(traceback.format_exc())
                await websocket.send(json.dumps(makeResponse("err", f"unexpected error: {str(e)}")))
        
        except websockets.exceptions.ConnectionClosed:
            # client disconnected
            activeConnections.removeConn(websocket)


async def handleAuthorise(websocket, msg):
    try:
        username = msg['username']
        password = creds.hashPw(msg['password'])
    except KeyError:
        await websocket.send(makeResponse(
            "err",
            "missing 'username' and/or 'password' keys (unauthorised)"
        ))
    except Exception as e:
        print(traceback.format_exc())
        await websocket.send(
            json.dumps(makeResponse(
                "err",
                f"unexpected error: {str(e)}"
            ))
        )

    # check if its logged in right
    if username == dbUsername and password == dbPassword:
        activeConnections.authoriseConnection(websocket)
        await websocket.send(makeResponse(
            "success",
            "authorised"
        ))
    else:
        await websocket.send(makeResponse(
            "err",
            "invalid username/password"
        ))

async def main():
    async with websockets.serve(handle, ip, port):
        # run forever
        await asyncio.Future()


activeConnections = ActiveConnections()
dbUsername, dbPassword = creds.getCreds()

def start(ip, port):
    asyncio.run(main(ip, port))