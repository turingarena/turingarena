from turingarena_impl.driver.language import Language
from .generator import JavaSkeletonCodeGen, JavaTemplateCodeGen
from .source import JavaAlgorithmSource

language = Language(
    name="java",
    extension=".java",
    source=JavaAlgorithmSource,
    skeleton_generator=JavaSkeletonCodeGen,
    template_generator=JavaTemplateCodeGen,
)
