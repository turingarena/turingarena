import os
import shutil


class DriverPreparer:

    def __init__(self, problem_preparer, driver, output_dir):
        self.problem_preparer = problem_preparer
        self.driver = driver
        self.output_dir = output_dir

    def prepare(self):
        shutil.copyfile(
            os.path.join(self.problem_preparer.definition_dir, self.driver.source),
            os.path.join(self.output_dir, "driver.cpp"),
        )

