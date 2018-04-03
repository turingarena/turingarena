from .executable import PythonAlgorithmExecutableScript
from .source import PythonAlgorithmSource
from .generator import PythonSkeletonCodeGen, PythonTemplateCodeGen
from turingarena.sandbox.languages.language import Language

language = Language(
    name="python",
    extension="py",
    source=PythonAlgorithmSource,
    executable=PythonAlgorithmExecutableScript,
    skeleton_generator=PythonSkeletonCodeGen,
    template_generator=PythonTemplateCodeGen,
)
