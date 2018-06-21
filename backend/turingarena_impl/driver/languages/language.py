import importlib
import os
import pkgutil
from collections import namedtuple

from turingarena_impl.loader import split_module


class UnknownFileExtension(Exception):
    pass


class Language(namedtuple("Language", [
    "name",
    "extension",
    "source",
    "skeleton_generator",
    "template_generator",
])):
    __slots__ = []

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
        raise ValueError(f"language {name} not supported by TuringArena")

    @classmethod
    def from_extension(cls, extension):
        for language in cls.languages():
            if language.extension == extension:
                return language
        raise UnknownFileExtension

    @staticmethod
    def from_source_name(source_name):
        mod_name, rel_path = split_module(source_name)
        base, ext = os.path.splitext(rel_path)
        return Language.from_extension(ext)
