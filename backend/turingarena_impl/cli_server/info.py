from turingarena_impl.driver.language import Language


def info_languages():
    print("Supported languages\n")
    print("Name\tExtension\tSupported for evaluator")
    print("----\t---------\t-----------------------")
    for language in Language.languages():
        print(f"{language.name}\t{language.extension}\t\t{'yes' if language.supported_for_evaluator else 'no'}")


def info_cmd(args):
    if args.what == "languages":
        info_languages()
