import logging
import os
import shutil

import turingarena.protocol.proxy.python.main as python_proxygen
from turingarena.protocol.skeleton import languages

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self, task, output_dir):
        self.task = task
        self.output_dir = output_dir

        self.interfaces_dir = os.path.join(self.output_dir, "protocol")
        self.runtime_dir = os.path.join(self.output_dir, "lib")

        self.generate()

    def generate(self):
        os.makedirs(self.output_dir, exist_ok=True)

        # cleanup
        shutil.rmtree(self.output_dir, ignore_errors=True)
        os.mkdir(self.output_dir)

        self.generate_interfaces_support()
        self.generate_proxy()

