from turingarena_impl.driver.language import Language

from .generator import PythonSkeletonCodeGen, PythonTemplateCodeGen
from .runner import PythonProgramRunner

language = Language(
    name="Python",
    extension=".py",
    ProgramRunner=PythonProgramRunner,
    skeleton_generator=PythonSkeletonCodeGen,
    template_generator=PythonTemplateCodeGen,
    supported_for_evaluator=True,
)
