import json
import logging

from werkzeug.wrappers import Request, Response

from turingarena.loggerinit import init_logger
import secrets

init_logger()
logger = logging.getLogger(__name__)


class Execution:

    def __init__(self, _id):
        self.id = _id

    def create(self, *, cmd):
        pass

    def response(self):
        return Response(
            status=200,
            response=json.dumps({
                "id": self.id,
            })
        )


def method_exec(request):
    execution = Execution(secrets.token_hex(32))

    execution.create(
        cmd=request.form["cmd"],
    )

    return execution.response()


def method_start(request):
    raise NotImplementedError


def method_attach(request):
    raise NotImplementedError


def method_wait(request):
    raise NotImplementedError


def method_import(request):
    raise NotImplementedError


def method_export(request):
    raise NotImplementedError


@Request.application
def api(request):
    try:
        if request.path == "/exec/create":
            return method_exec(request)
        if request.path == "/exec/start":
            return method_start(request)
        if request.path == "/exec/attach":
            return method_attach(request)
        if request.path == "/exec/wait":
            return method_wait(request)
        if request.path == "/data/import":
            return method_import(request)
        if request.path == "/data/export":
            return method_export(request)
        return Response(status=404, response="invalid path")
    except Exception as e:
        logger.exception(e)
        return Response(status=500, response=str(e))
