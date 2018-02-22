import logging
import os
import shutil

from . import cpp, python

logger = logging.getLogger(__name__)

languages = {
    "cpp":    cpp.generate_skeleton,
    "python": python.generate_skeleton,
}


class SkeletonGenerator:
    def __init__(self, protocol, dest_dir):
        self.protocol = protocol
        self.dest_dir = dest_dir

        self.generate()

    def generate(self):
        os.makedirs(self.dest_dir, exist_ok=True)
        shutil.rmtree(self.dest_dir)

        os.mkdir(self.dest_dir)
        for interface in self.protocol.body.scope.interfaces.values():
            self.generate_skeleton_interface(interface)

    def generate_skeleton_interface(self, interface):
        interface_dir = self.make_interface_dir(interface)
        os.mkdir(interface_dir)
        for language in languages.keys():
            self.generate_skeleton_language(interface=interface, language=language)

    def generate_skeleton_language(self, *, interface, language):
        language_dir = self.make_language_dir(interface, language)
        os.mkdir(language_dir)
        logger.info(f"Generating support for interface '{interface.name}' ({language})")
        languages[language](
            interface=interface,
            dest_dir=language_dir,
        )

    def make_interface_dir(self, interface):
        return os.path.join(self.dest_dir, interface.name)

    def make_language_dir(self, interface, language):
        return os.path.join(self.make_interface_dir(interface), language)


generate_skeleton = SkeletonGenerator
