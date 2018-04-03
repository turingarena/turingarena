from .executable import JavaScriptAlgorithmExecutableScript
from .source import JavascriptAlgorithmSource
from .generator import JavaScriptSkeletonCodeGen, JavaScriptTemplateCodeGen
from turingarena.sandbox.languages.language import Language

language = Language(
    name="javascript",
    extension="js",
    source=JavascriptAlgorithmSource,
    executable=JavaScriptAlgorithmExecutableScript,
    skeleton_generator=JavaScriptSkeletonCodeGen,
    template_generator=JavaScriptTemplateCodeGen,
)
