import sys
import subprocess as sp

from ghooklistener import Listener, PayloadType, HandleFuncReturnType
from http import HTTPStatus
from os import path


CONFIG = {"repos_dir": "", "repos": []}


def handlefunc(data: PayloadType) -> HandleFuncReturnType:
    try:
        repo_name = data["repository"]["name"]
        ref = data["ref"]
        forced = data["forced"]
    except (KeyError, TypeError) as unwrap_err:
        print(f"Invalid payload {unwrap_err}")
        return "Invalid payload\n", HTTPStatus.BAD_REQUEST

    if repo_name not in CONFIG['hosted_repos']:
        print(f"[BadRequest] Unsupported repository {repo_name}")
        return "Invalid payload\n", HTTPStatus.BAD_REQUEST

    clone_loc = path.join(CONFIG['repos_dir'], repo_name)

    if ref != "refs/heads/master":
        print("Not master branch.  Not updating.")
        return "OK\n", HTTPStatus.OK

    # if it was a force push, we will have to fetch and reset
    if pull(clone_loc, forced):
        return "OK\n", HTTPStatus.OK

    return "Internal server error\n", HTTPStatus.INTERNAL_SERVER_ERROR


def pull(cloneloc: str, force: bool) -> bool:
    if force:
        print("Force pushes not yet supported")
        print("Doing normal push")

    if not path.exists(cloneloc):
        print(f"Invalid git directory: {cloneloc}")
        return False

    p = sp.run(["git", "pull"],
               stdout=sp.PIPE, stderr=sp.PIPE,
               cwd=cloneloc, encoding="utf-8")

    stdout, stderr = p.stdout.strip(), p.stderr.strip()
    print(f"Out: {stdout}")
    print(f"Err: {stderr}")

    return not p.returncode


def main():
    address = ":0"
    secret_token = b''

    if len(sys.argv) < 1 or not path.exists(sys.argv[1]):
        print("[Error] Provide git repositories directory as first argument")
        exit(-1)

    repos_dir = sys.argv[1]
    if len(sys.argv) > 2:
        secret_token = sys.argv[2].encode('utf-8')
    if len(sys.argv) > 3:
        address = sys.argv[3]

    CONFIG['repos_dir'] = repos_dir
    CONFIG['hosted_repos'] = ["odml-terminologies", "odml-templates"]

    print("Setting up listener for cloner handler")
    clonelistener = Listener("cloner", handlefunc=handlefunc, secret_token=secret_token)
    clonelistener.rundev(address)


if __name__ == "__main__":
    main()
