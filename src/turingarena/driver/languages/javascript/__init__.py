from turingarena.driver.language import Language

disabled_language = Language(
    name="javascript",
    extension=".js",
    ProgramRunner=None,
    Generator=None,
    supported_for_evaluator=False,
)
