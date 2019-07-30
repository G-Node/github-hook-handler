import sys
from ghooklistener import Listener, PayloadType, HandleFuncReturnType


def handlefunc(data: PayloadType) -> HandleFuncReturnType:
    print(data)
    print("Received data")
    return True, "OK"


def main():
    address = ":0"
    if len(sys.argv) > 1:
        address = sys.argv[1]
    print("Setting up listener for cloner handler")
    clonelistener = Listener("cloner", handlefunc=handlefunc)
    clonelistener.rundev(address)


if __name__ == "__main__":
    main()
