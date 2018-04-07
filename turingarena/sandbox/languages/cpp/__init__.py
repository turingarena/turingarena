from turingarena.sandbox.languages.language import Language
from .executable import ElfAlgorithmExecutable
from .generator import CppSkeletonCodeGen, CppTemplateCodeGen
from .source import CppAlgorithmSource

language = Language(
    name="c++",
    extension=".cpp",
    source=CppAlgorithmSource,
    executable=ElfAlgorithmExecutable,
    skeleton_generator=CppSkeletonCodeGen,
    template_generator=CppTemplateCodeGen,
)
