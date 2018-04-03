from .executable import ElfAlgorithmExecutable
from .source import CppAlgorithmSource
from .generator import CppSkeletonCodeGen, CppTemplateCodeGen
from turingarena.sandbox.languages.language import Language

language = Language(
    name="c++",
    extension="cpp",
    source=CppAlgorithmSource,
    executable=ElfAlgorithmExecutable,
    skeleton_generator=CppSkeletonCodeGen,
    template_generator=CppTemplateCodeGen,
)
