from turingarena.driver.language import Language

from .generator import GoSkeletonCodeGen, GoTemplateCodeGen
from .runner import GoProgramRunner

language = Language(
    name="Go",
    extension=".go",
    ProgramRunner=GoProgramRunner,
    skeleton_generator=GoSkeletonCodeGen,
    template_generator=GoTemplateCodeGen,
    supported_for_evaluator=False,
)
