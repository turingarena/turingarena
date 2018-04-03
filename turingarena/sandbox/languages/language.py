import os
import pkgutil
import importlib

from collections import namedtuple


class Language(namedtuple("Language", [
    "name",
    "extension",
    "source",
    "executable",
    "skeleton_generator",
    "template_generator",
])):
    __slots__ = []

    def __new__(cls, *args, **kwargs):
        if args:
            if args[0][0] == ".":
                return cls.from_extension(args[0][1:])
            return cls.from_name(args[0])
        return super().__new__(cls, *args, **kwargs)

    @staticmethod
    def languages():
        mod_name = os.path.splitext(__name__)[0]

        languages = []
        for mod in pkgutil.iter_modules(importlib.import_module(mod_name).__path__):
            if mod.ispkg:
                mod = importlib.import_module(f"{mod_name}.{mod.name}")
                try:
                    languages.append(getattr(mod, "language"))
                except AttributeError:
                    pass
        return languages

    @classmethod
    def from_name(cls, name):
        for language in cls.languages():
            if language.name == name:
                return language
        raise RuntimeError(f"language {name} not supported by TuringArena")

    @classmethod
    def from_extension(cls, extension):
        for language in cls.languages():
            if language.extension == extension:
                return language
        raise RuntimeError(f"no language with extension{extension} is supported by TuringArena")
