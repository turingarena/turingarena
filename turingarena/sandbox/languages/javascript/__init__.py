from turingarena.sandbox.languages.language import Language
from .executable import JavaScriptAlgorithmExecutableScript
from .generator import JavaScriptSkeletonCodeGen, JavaScriptTemplateCodeGen
from .source import JavascriptAlgorithmSource

language = Language(
    name="javascript",
    extension=".js",
    source=JavascriptAlgorithmSource,
    executable=JavaScriptAlgorithmExecutableScript,
    skeleton_generator=JavaScriptSkeletonCodeGen,
    template_generator=JavaScriptTemplateCodeGen,
)
