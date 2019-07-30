import json
from typing import Callable, Optional, Dict, Any, Tuple
from flask import Flask, request, Response


PayloadType = Dict[str, Any]
HandleFuncReturnType = Tuple[bool, str]


class Listener(object):

    def __init__(self, name: str, handlefunc: Callable[[PayloadType], None]):
        self.app = Flask(name)
        self.handlefunc = handlefunc
        self.app.add_url_rule("/", view_func=self.hook_receive,
                              methods=["POST"])

    def hook_receive(self):
        # TODO: Handle malformed data and other stuff
        data: PayloadType = json.loads(request.data)

        if "hook_id" in data:
            # Ping event: New hook added
            ok, message = self._report_new_hook(data)
            code = 200 if ok else 400
        elif False:
            ok, message = self.handlefunc(data)
            if ok:
                code = 200
            else:
                code = 500
        else:
            message = "Unknown payload"
            code = 400
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
        except KeyError as ke:
            key = str(ke.args[0])
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
