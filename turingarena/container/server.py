import json
import logging
import os
import secrets
import subprocess

from werkzeug.wrappers import Request, Response

from turingarena.cli.loggerinit import init_logger

init_logger()
logger = logging.getLogger(__name__)


class Execution:

    def __init__(self, _id):
        self.id = _id
        self.execution_dir = "/tmp/execution-" + self.id
        self.cmd_filename = "{}/cmd.txt".format(self.execution_dir)
        self.stdout_filename = "{}/stdout.pipe".format(self.execution_dir)
        self.stderr_filename = "{}/stderr.pipe".format(self.execution_dir)

    def create(self, *, cmd):
        os.mkdir(self.execution_dir)

        with open(self.cmd_filename, "w") as f:
            print(cmd, file=f)

        os.mkfifo(self.stdout_filename)
        os.mkfifo(self.stderr_filename)

    def start(self):
        with open(self.cmd_filename) as f:
            cmd = f.readline().strip()

        with open(self.stdout_filename, "w") as stdout, open(self.stderr_filename, "w") as stderr:
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=stdout,
                stderr=stderr,
            )

    def attach(self, which):
        if which == "stdout":
            filename = self.stdout_filename
        elif which == "stderr":
            filename = self.stderr_filename
        else:
            raise ValueError

        return Response(response=open(filename))

    def response(self):
        return Response(
            status=200,
            response=json.dumps({
                "id": self.id,
            }),
            mimetype="application/json",
        )


def method_create(request):
    execution = Execution(secrets.token_hex(32))

    execution.create(
        cmd=request.form["cmd"],
    )

    return execution.response()


def method_start(request):
    execution = Execution(request.form["id"])
    execution.start()
    return execution.response()


def method_attach(request):
    execution = Execution(request.form["id"])
    return execution.attach(which=request.form["which"])


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
            return method_create(request)
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
