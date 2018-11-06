try:
    from .build_version import VERSION
except ImportError:
    VERSION = "UNKNOWN"
