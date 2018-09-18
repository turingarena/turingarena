try:
    from .build_version import VERSION
except ImportError:
    VERSION = "0.0.0.dev0+unknown"
