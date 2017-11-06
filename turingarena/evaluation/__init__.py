import json
import subprocess
from tempfile import TemporaryDirectory

from turingarena.common import ImmutableObject, TupleLikeObject


class Task(TupleLikeObject):
    __slots__ = ["meta_command"]

    def __init__(self, meta_command):
        super().__init__(meta_command=meta_command)

    def resolve(self):
        with TemporaryDirectory() as dir:
            result = subprocess.run(
                self.meta_command,
                chdir=dir,
                shell=True,
                stdout=subprocess.PIPE,
            )
        return json.loads(
            result.stdout,
            cls=TaskDescription,
        )


class TaskDescription(ImmutableObject):
    __slots__ = ["command", "dependencies"]

    def to_json(self):
        return json.dumps({
            "command": self.command,
            "dependencies": [
                d.meta_command
                for d in self.dependencies
            ]
        }, indent=4)
