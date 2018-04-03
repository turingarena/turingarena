from .executable import JavaAlgorithmExecutable
from .source import JavaAlgorithmSource
from .generator import JavaSkeletonCodeGen, JavaTemplateCodeGen
from turingarena.sandbox.languages.language import Language

language = Language(
    name="java",
    extension="java",
    source=JavaAlgorithmSource,
    executable=JavaAlgorithmExecutable,
    skeleton_generator=JavaSkeletonCodeGen,
    template_generator=JavaTemplateCodeGen,
)
