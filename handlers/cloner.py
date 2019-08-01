import sys
import subprocess as sp
from ghooklistener import Listener, PayloadType, HandleFuncReturnType


def handlefunc(data: PayloadType) -> HandleFuncReturnType:
    try:
        ref = data["ref"]
        forced = data["forced"]

    except (KeyError, TypeError) as unwrap_err:
        return False, f"Invalid payload: {str(unwrap_err)}"

    if ref != "refs/heads/master":
        print("Not master branch.  Not updating.")
        return True, "OK"

    # if it was a force push, we will have to fetch and reset
    if pull(forced):
        return True, "OK"

    return False, "Pull failed"


def pull(force: bool) -> bool:
    if force:
        print("Force pushes not yet supported")
        print("Doing normal push")
    cloneloc = "/tmp/place"
    p = sp.run(["git", "pull"],
               stdout=sp.PIPE, stderr=sp.PIPE,
               cwd=cloneloc, encoding="utf-8")
    stdout, stderr = p.stdout.strip(), p.stderr.strip()
    print(f"Out: {stdout}")
    print(f"Err: {stderr}")

    return not p.returncode


def main():
    address = ":0"
    if len(sys.argv) > 1:
        address = sys.argv[1]
    print("Setting up listener for cloner handler")
    clonelistener = Listener("cloner", handlefunc=handlefunc)
    clonelistener.rundev(address)


if __name__ == "__main__":
    main()
