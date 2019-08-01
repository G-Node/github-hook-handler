import hmac
import json

from flask import Flask, request, Response
from hashlib import sha1
from http import HTTPStatus
from os import path
from typing import Callable, Optional, Dict, Any, Tuple, List


PayloadType = Dict[str, Any]
HandleFuncReturnType = Tuple[bool, str]


class Listener(object):

    def __init__(self, name: str, handlefunc: Callable[[PayloadType], None],
                 secret_token: bytes, repos_dir: str, hosted_repos: List[str]):
        self.app = Flask(name)
        self.handlefunc = handlefunc
        self.app.add_url_rule("/", view_func=self.hook_receive,
                              methods=["POST"])
        self.secret_token = secret_token
        self.repos_dir = repos_dir
        self.hosted_repos = hosted_repos

    def _check_signature(self, signature, data):
        """
        _check_signature computes the sha1 hexdigest of the request payload with
        the applications secret key and compares it to the requests hexdigest signature.

        :param signature: hexdigest signature of the request
        :param data: bytes object containing the request payload
        :return: boolean result of the digest comparison
        """

        hashed = hmac.new(self.secret_token, data, sha1)
        sig_check = f"sha1={hashed.hexdigest()}"

        return hmac.compare_digest(signature, sig_check)

    def hook_receive(self):
        # Expect the worst
        message = "Bad request\n"
        try:
            event_type = request.headers["X-GitHub-Event"]
            signature = request.headers["X-Hub-Signature"]
        except KeyError as err:
            print(f"Missing request header: {err}\n")
            return Response(response=message, status=HTTPStatus.BAD_REQUEST)

        if not request.data:
            print("[BadRequest] Missing payload\n")
            return Response(response=message, status=HTTPStatus.BAD_REQUEST)

        if not self._check_signature(signature, request.data):
            print("[BadRequest] Signature mismatch\n")
            return Response(response=message, status=HTTPStatus.BAD_REQUEST)

        try:
            data: PayloadType = json.loads(request.data)
        except json.decoder.JSONDecodeError as err:
            print(f"[BadRequest] JsonDecode error: {err}")
            return Response(response=message, status=HTTPStatus.BAD_REQUEST)

        if event_type == "ping":
            # Ping event: New hook added
            ok, message = self._report_new_hook(data)
            code = HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST
        elif event_type == "push":
            # Identify the repository that needs to be pulled
            try:
                repo_name = data["repository"]["name"]
            except (KeyError, TypeError) as err:
                print(f"[BadRequest] Missing payload information: {err}\n")
                return Response(response=message, status=HTTPStatus.BAD_REQUEST)

            if repo_name not in self.hosted_repos:
                print(f"[BadRequest] Unsupported repository {repo_name}\n")
                return Response(response=message, status=HTTPStatus.BAD_REQUEST)

            clone_dir = path.join(self.repos_dir, repo_name)

            # assume push event
            ok, message = self.handlefunc(clone_dir, data)
            # ToDo: currently the fail status is still not correct if
            # the payload has missing information - should be BAD_REQUEST in this case.
            code = HTTPStatus.OK if ok else HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            message = f"Unknown event type: {event_type}"
            code = HTTPStatus.BAD_REQUEST

        message = f"{message}\n"
        return Response(response=message, status=code)

    def _report_new_hook(self, data: PayloadType) -> HandleFuncReturnType:
        # read keys but return 400 if any expected keys are missing
        try:
            zen = data["zen"]
            hook_id = data["hook_id"]

            hook_config = data["hook"]
            events = hook_config["events"]
            hook_url = hook_config["url"]
            created_at = hook_config["created_at"]
        except KeyError as err:
            key = str(err.args[0])
            msg = f"Missing expected key in payload: {key}"
            print(msg)
            return False, msg

        print(f"New hook with ID {hook_id} has been set up:")
        print(f" - Hook URL: {hook_url}")
        print(f" - Hook events: {', '.join(events)}")
        print(f" - Creation date: {created_at}")
        print(f"GH zen: {zen}")
        return True, "Pong"

    def rundev(self, address: Optional[str] = None):
        host: Optional[str] = None
        port: Optional[int] = None
        if address:
            addparts = address.split(":")
            host = addparts[0]
            try:
                port = int(addparts[1])
                if port > 65536:
                    raise ValueError
            except ValueError:
                print(f"Port {port} invalid. Falling back to defaults")
                host = None
                port = None

        self.app.run(host=host, port=port, debug=True)
