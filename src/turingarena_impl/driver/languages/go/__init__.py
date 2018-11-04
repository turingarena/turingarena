from turingarena_impl.driver.language import Language

from .generator import GoSkeletonCodeGen, GoTemplateCodeGen
from .source import GoAlgorithmSource

language = Language(
    name="Go",
    extension=".go",
    source=GoAlgorithmSource,
    skeleton_generator=GoSkeletonCodeGen,
    template_generator=GoTemplateCodeGen,
    supported_for_evaluator=False,
)
