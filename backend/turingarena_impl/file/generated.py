import os
from collections import namedtuple
from functools import lru_cache

from future.moves import sys

from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language

INTERFACE_TXT = "interface.txt"


class PackGeneratedDirectory(namedtuple("PackGeneratedDirectory", ["working_directory"])):
    @property
    @lru_cache(None)
    def targets(self):
        return list(self._generate_targets())

    def _generate_targets(self):
        for dirpath, dirnames, filenames in os.walk(self.working_directory):
            relpath = os.path.relpath(dirpath, self.working_directory)
            if INTERFACE_TXT in filenames:
                yield from self._generate_interface_targets(dirpath, relpath)

    def _generate_interface_targets(self, abspath, relpath):
        for lang in Language.languages():
            interface_path = os.path.join(abspath, INTERFACE_TXT)
            yield (
                os.path.join(relpath, f"skeleton{lang.extension}"),
                self._create_interface_code_generator(interface_path, lang.skeleton_generator()),
            )
            yield (
                os.path.join(relpath, f"template{lang.extension}"),
                self._create_interface_code_generator(interface_path, lang.template_generator()),
            )

    def _create_interface_code_generator(self, interface_path, code_generator):
        def generator(outfile):
            with open(interface_path) as f:
                interface = InterfaceDefinition.compile(f.read())
            code_generator.generate_to_file(interface, outfile)

        return generator

    def cat_file(self, path):
        for p, generator in self.targets:
            if p == path:
                return generator(sys.stdout)
        raise FileNotFoundError(path)
