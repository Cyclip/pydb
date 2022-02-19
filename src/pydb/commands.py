import json

from exceptions import *

COMMANDS = [
    "createTable",
    "dropTable",
]

async def verifyCommand(cmd):
    if cmd['command'] not in COMMANDS:
        raise UnknownCommand