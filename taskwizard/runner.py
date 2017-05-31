import tempfile

from taskwizard.supervisor import Supervisor


class ModuleRunner:

    def __init__(self, executable_path, algorithms):
        self.executable_path = executable_path
        self.algorithms = algorithms

    def run(self):
        with tempfile.TemporaryDirectory() as sandbox_dir:
            Supervisor(self.executable_path, sandbox_dir, self.algorithms).run()
