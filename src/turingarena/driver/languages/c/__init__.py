from turingarena.driver.language import Language

from .generator import CSkeletonCodeGen, CTemplateCodeGen
from .runner import CProgramRunner

language = Language(
    name="C",
    extension=".c",
    ProgramRunner=CProgramRunner,
    skeleton_generator=CSkeletonCodeGen,
    template_generator=CTemplateCodeGen,
    supported_for_evaluator=False,
)
