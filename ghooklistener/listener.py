from flask import Flask, request, Response
from typing import Callable, Optional, Dict, Any, Tuple


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
        data = request.data
        ok, message = self.handlefunc(data)
        if ok:
            code = 200
        else:
            code = 500
        return Response(response=message, status=code)

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
