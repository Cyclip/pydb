import websockets
import asyncio
import json
import traceback

import commands
from exceptions import *

activeConnections = []

def makeResponse(respType, message):
    return json.dumps({
        "response": respType,
        "message": message,
    })


async def keepAlive(websocket):
    global activeConnections

    while True:
        try:
            test = await websocket.ping()
            await test
        except websockets.exceptions.ConnectionClosed:
            # client disconnected
            activeConnections.remove(websocket.id)
            print("client disconnected")
            break

        await asyncio.sleep(1)


async def handle(websocket):
    global activeConnections

    asyncio.create_task(keepAlive(websocket))

    async for msg in websocket:
        try:
            # build a command

            if websocket.id in activeConnections:
                print("already in")
            else:
                activeConnections.append(websocket.id)
                print("appended:", activeConnections)

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
            activeConnections.remove(websocket.id)


async def main():
    async with websockets.serve(handle, "localhost", 2000):
        # run forever
        await asyncio.Future()


asyncio.run(main())