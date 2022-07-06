"""

Module containing all exceptions

"""

__all__ = (
    'MutualExclusionError',
    'MissingRequiredPathError',
    'NotAFileError',
    'InvalidImageTypeError',
)

class MutualExclusionError(Exception):
    pass

class MissingRequiredPathError(Exception):
    pass

class InvalidImageTypeError(Exception):
    pass

class NotAFileError(Exception):
    pass