from turingarena.sandbox.languages.language import Language
from .executable import JavaAlgorithmExecutable
from .generator import JavaSkeletonCodeGen, JavaTemplateCodeGen
from .source import JavaAlgorithmSource

language = Language(
    name="java",
    extension=".java",
    source=JavaAlgorithmSource,
    executable=JavaAlgorithmExecutable,
    skeleton_generator=JavaSkeletonCodeGen,
    template_generator=JavaTemplateCodeGen,
)
