"""
Example hook handler script.  To write your own handler, copy this file and
replace the 'handlefunc' function with your own code.  The function should
accept the hook payload through the single argument 'data' (PayloadType),
perform a task, and return a boolean indicating success (True) or failure
(False) and a message as a string (empty strings are allowed).
"""
import sys
from ghooklistener import Listener, PushPayloadType, HandleFuncReturnType


# Example handlefunc simply prints the data and returns OK
def handlefunc(data: PushPayloadType) -> HandleFuncReturnType:
    print("Received data")
    print(data)
    return True, "OK"


# Set up a listener instance and run in dev mode
def main():
    address = ":0"
    if len(sys.argv) > 1:
        address = sys.argv[1]
    print("Setting up listener for cloner handler")
    clonelistener = Listener("cloner", handlefunc=handlefunc)
    clonelistener.rundev(address)


if __name__ == "__main__":
    main()
