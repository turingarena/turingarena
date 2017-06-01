from taskwizard.generation.types import BaseTypeExtractor


def generate_base_type(type):
    base_type = BaseTypeExtractor().visit(type)
    return {
        "int": "int",
        "int64": "long long int",
    }[base_type]
