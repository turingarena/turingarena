from turingarena_impl.driver.language import Language
from .generator import JavaSkeletonCodeGen, JavaTemplateCodeGen
from .source import JavaAlgorithmSource

language = Language(
    name="Java",
    extension=".java",
    source=JavaAlgorithmSource,
    skeleton_generator=JavaSkeletonCodeGen,
    template_generator=JavaTemplateCodeGen,
    supported_for_evaluator=False,
)
