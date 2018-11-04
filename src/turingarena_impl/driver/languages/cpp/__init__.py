from turingarena_impl.driver.language import Language

from .generator import CppSkeletonCodeGen, CppTemplateCodeGen
from .runner import CppProgramRunner

language = Language(
    name="C++",
    extension=".cpp",
    ProgramRunner=CppProgramRunner,
    skeleton_generator=CppSkeletonCodeGen,
    template_generator=CppTemplateCodeGen,
    supported_for_evaluator=True,
)
