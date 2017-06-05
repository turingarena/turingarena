import os

from taskwizard import grammar


class TaskParser:

    def __init__(self, definition_dir):
        self.definition_dir = definition_dir
        self.task_file_path = os.path.join(definition_dir, "task.txt")

    def parse(self):
        return grammar.parse(open(self.task_file_path).read(), rule="unit")
