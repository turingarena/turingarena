import tempfile

from turingarena.sandbox.server import SandboxManagerServer


class ModuleRunner:

    def __init__(self, args, algorithms):
        self.args = args
        self.algorithms = algorithms

    def run(self):
        with tempfile.TemporaryDirectory() as sandbox_dir:
            SandboxManagerServer(self.args, sandbox_dir, self.algorithms).run()
