import tempfile

from taskwizard.supervisor import Supervisor


class ModuleRunner:

    def __init__(self, args, algorithms):
        self.args = args
        self.algorithms = algorithms

    def run(self):
        with tempfile.TemporaryDirectory() as sandbox_dir:
            Supervisor(self.args, sandbox_dir, self.algorithms).run()
