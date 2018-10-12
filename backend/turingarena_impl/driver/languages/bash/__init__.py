from turingarena_impl.driver.language import Language
from .generator import BashSkeletonCodeGen, BashTemplateCodeGen
from .source import BashAlgorithmSource

language = Language(
    name="bash",
    extension=".sh",
    source=BashAlgorithmSource,
    skeleton_generator=BashSkeletonCodeGen,
    template_generator=BashTemplateCodeGen,
    supported_for_evaluator=False,
)
