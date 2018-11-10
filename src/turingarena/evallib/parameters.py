from turingarena.evallib.metadata import load_metadata


class Parameters:
    def __getitem__(self, item):
        return load_metadata().get("parameters", {})[item]

    def __getattr__(self, item):
        return self[item]
