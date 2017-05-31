import tempfile

from taskwizard.supervisor import Supervisor


class ModuleRunner:

    def __init__(self, executable_path):
        self.executable_path = executable_path

    def run(self):
        with tempfile.TemporaryDirectory() as sandbox_dir:
            Supervisor(self.executable_path, sandbox_dir).run()
