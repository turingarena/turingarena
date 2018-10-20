from turingarena_impl.driver.language import Language
from turingarena_impl.driver.languages.c.generator import CSkeletonCodeGen, CTemplateCodeGen
from turingarena_impl.driver.languages.c.source import CAlgorithmSource


language = Language(
    name="C",
    extension=".c",
    source=CAlgorithmSource,
    skeleton_generator=CSkeletonCodeGen,
    template_generator=CTemplateCodeGen,
    supported_for_evaluator=True,
)
