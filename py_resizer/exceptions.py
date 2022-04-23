"""

Module containing all exceptions

"""

class MutualExclusionError(Exception):
    pass

class MissingRequiredPathError(Exception):
    pass

class InvalidImageTypeError(Exception):
    pass

class NotAFileError(Exception):
    pass