import os
from collections import namedtuple
from functools import lru_cache

from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language

INTERFACE_TXT = "interface.txt"


class PackGeneratedDirectory(namedtuple("PackGeneratedDirectory", ["work_dir"])):
    @property
    @lru_cache(None)
    def targets(self):
        return list(self._generate_targets())

    def _create_text_generator(self, path):
        def generate(outfile):
            with open(path) as f:
                outfile.write(f.read())

        return generate

    def _generate_targets(self):
        for dirpath, dirnames, filenames in os.walk(self.work_dir):
            relpath = os.path.relpath(dirpath, self.work_dir)
            if INTERFACE_TXT in filenames:
                yield from self._generate_interface_targets(dirpath, relpath)
            if "statement.md" in filenames:
                path = os.path.join(dirpath, "statement.md")
                yield (os.path.join(relpath, "statement.md"), self._create_text_generator(path))
            elif "README.md" in filenames:
                path = os.path.join(dirpath, "README.md")
                yield (os.path.join(relpath, "statement.md"), self._create_text_generator(path))

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

    def cat_file(self, path, *, file):
        for p, generator in self.targets:
            if p == path:
                return generator(file)
        raise FileNotFoundError(path)
