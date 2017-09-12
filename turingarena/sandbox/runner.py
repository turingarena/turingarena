import tempfile

from turingarena.sandbox.sandboxmanager import SandboxManager


class ModuleRunner:

    def __init__(self, args, algorithms):
        self.args = args
        self.algorithms = algorithms

    def run(self):
        with tempfile.TemporaryDirectory() as sandbox_dir:
            SandboxManager(self.args, sandbox_dir, self.algorithms).run()
