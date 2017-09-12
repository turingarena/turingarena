import os
import shutil


class ModulePreparer:

    def __init__(self, problem_preparer, module, output_dir):
        self.problem_preparer = problem_preparer
        self.module = module
        self.output_dir = output_dir

    def prepare(self):
        shutil.copyfile(
            os.path.join(self.problem_preparer.definition_dir, self.module.source),
            os.path.join(self.output_dir, "module.cpp"),
        )

