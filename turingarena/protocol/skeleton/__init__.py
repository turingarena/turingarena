import logging
import os
import shutil

from . import cpp, python

logger = logging.getLogger(__name__)

languages = {
    "cpp": cpp.generate_skeleton,
    "python": python.generate_skeleton,
}


class SkeletonGenerator:
    def __init__(self, interface_definition, dest_dir):
        self.interface_definition = interface_definition
        self.dest_dir = dest_dir

        self.generate()

    def generate(self):
        os.makedirs(self.dest_dir, exist_ok=True)
        shutil.rmtree(self.dest_dir)

        os.mkdir(self.dest_dir)

        for language in languages.keys():
            self.generate_skeleton_language(language)

    def generate_skeleton_language(self, language):
        language_dir = self.make_language_dir(language)
        os.mkdir(language_dir)
        languages[language](
            interface_definition=self.interface_definition,
            dest_dir=language_dir,
        )

    def make_language_dir(self, language):
        return os.path.join(self.dest_dir, language)


generate_skeleton = SkeletonGenerator
