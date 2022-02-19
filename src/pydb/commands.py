import json

from exceptions import *

COMMANDS = [
    "createTable",
    "dropTable",
]

async def getCommand(cmd):
    cmd = json.loads(cmd)

    if cmd['command'] not in COMMANDS:
        raise UnknownCommand

    return cmd