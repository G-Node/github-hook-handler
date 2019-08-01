import sys
import subprocess as sp

from ghooklistener import Listener, PayloadType, HandleFuncReturnType
from os import path


GIT_DIR = "/tmp/git_repos"
SUPPORTED_REPOS = ["odml-terminologies", "odml-templates"]


def handlefunc(data: PayloadType) -> HandleFuncReturnType:
    try:
        repo_name = data["repository"]["name"]
        ref = data["ref"]
        forced = data["forced"]

    except (KeyError, TypeError) as unwrap_err:
        return False, f"Invalid payload: {str(unwrap_err)}"

    if repo_name not in SUPPORTED_REPOS:
        print(f"Unsupported repository {repo_name}")
        return False, "Pull failed"

    if ref != "refs/heads/master":
        print("Not master branch.  Not updating.")
        return True, "OK"

    # if it was a force push, we will have to fetch and reset
    if pull(repo_name, forced):
        return True, "OK"

    return False, "Pull failed"


def pull(repo_name: str, force: bool) -> bool:
    if force:
        print("Force pushes not yet supported")
        print("Doing normal push")

    cloneloc = path.join(GIT_DIR, repo_name)

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
    if len(sys.argv) > 1:
        address = sys.argv[1]
    if len(sys.argv) > 2:
        secret_token = sys.argv[2].encode('utf-8')

    print("Setting up listener for cloner handler")
    clonelistener = Listener("cloner", secret_token, handlefunc=handlefunc)
    clonelistener.rundev(address)


if __name__ == "__main__":
    main()
