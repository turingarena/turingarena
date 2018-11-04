from turingarena_impl.driver.language import Language

from .generator import JavaSkeletonCodeGen, JavaTemplateCodeGen
from .runner import JavaProgramRunner

language = Language(
    name="Java",
    extension=".java",
    ProgramRunner=JavaProgramRunner,
    skeleton_generator=JavaSkeletonCodeGen,
    template_generator=JavaTemplateCodeGen,
    supported_for_evaluator=False,
)
