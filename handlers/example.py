"""
Example hook handler script.  To write your own handler, copy this file and
replace the 'handlefunc' function with your own code.  The function should
accept the hook payload through the single argument 'data' (PayloadType),
perform a task, and return a boolean indicating success (True) or failure
(False) and a message as a string (empty strings are allowed).
"""
import sys

from http import HTTPStatus

from ghooklistener import Listener, PayloadType, HandleFuncReturnType


# Example handlefunc simply prints the data and returns OK
def handlefunc(data: PayloadType) -> HandleFuncReturnType:
    print("Received data")
    print(data)
    return "OK\n", HTTPStatus.OK


def create_app(secret_token: str):
    print("Setting up listener for example handler")
    secret_token = secret_token.encode('utf-8')
    clonelistener = Listener("example", handlefunc=handlefunc, secret_token=secret_token)

    return clonelistener


# Set up a listener instance and run in dev mode
def main():
    address = ":0"
    secret_token = b''

    if len(sys.argv) > 1:
        address = sys.argv[1]
    if len(sys.argv) > 2:
        secret_token = sys.argv[2]

    print("Setting up listener for example handler")
    listener = create_app(secret_token)
    listener.rundev(address)


if __name__ == "__main__":
    main()
