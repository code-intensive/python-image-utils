from typing import Any
from image_utils.config import settings


def get_supported_extensions_as_str() -> str:
    return ', '.join(settings.SUPPORTED_EXTENSIONS[:-1]) + ' or ' + settings.SUPPORTED_EXTENSIONS[-1]

def print_if_verbose(value: Any) -> None:
    if settings.VERBOSE:
        print(value)
    