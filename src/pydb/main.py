#!/usr/bin/python3

import sys
import argparse

import server
import database

# ---------- CONSTANTS ----------
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 3200
# -------------------------------



def main():
    """Start server"""
    parser = argparse.ArgumentParser(
        prog="pydb",
        usage="%(prog)s [options]",
        description="Python implemented database",
        epilog="〈 This project may not be secure and shouldn't be used in production 〉"
    )
    
    parser.add_argument(
        "-i",
        "--ip",
        metavar="ip",
        type=str,
        help="The ip of the server",
        default="localhost"
    )

    parser.add_argument(
        "-p",
        "--port",
        metavar="port",
        type=int,
        help="The port of the server",
        default=2050,
        choices=(1024, 65535)
    )

    args = parser.parse_args()
    
    database.init()

    server.start(
        args.ip,
        args.port
    )


if __name__ == "__main__":
	sys.exit(main())