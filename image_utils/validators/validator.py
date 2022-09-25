from pathlib import Path
from typing import Tuple, Union

from image_utils.core.exceptions import *
from image_utils.config import settings
from image_utils.validators.base import IValidator
from image_utils.core.utils import get_supported_extensions_as_str


class Validator(IValidator):
    def validate_file_extensions(self, file_: Path) -> None:
        if not file_.suffix.lower()[1:] in settings.SUPPORTED_EXTENSIONS:
            raise InvalidImageTypeError(
                'The image file extension is not supported, '
                F'supported extensions must be one of the following { get_supported_extensions_as_str() }')

    def validate_path(self, path: Union[Path, str]) -> Path:
        """ Validates the existence of the provided path """

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                F'{ path } was not found in your path, kindly review the path provided')

        return path

    def validate_file(self, path: Union[Path, str]) -> Path:
        """ Carries out validation on the file provided """

        path = self.validate_path(path)

        if not path.is_file():
            raise NotAFileError(
                F'{ path } exists but is not a file, kindly pass a valid file path')

        self.validate_file_extensions(path)

        return path


    def validate_directory(self, path: Union[Path, str]) -> Path:
        """ Carries out validation on the directory provided """

        path = self.validate_path(path)

        if not path.is_dir():
            raise NotADirectoryError(
                F'{ path } exists but is not a directory, kindly pass a valid directory path')
        
        return path


    def validate_path_args(self, *,
                           img_paths: Union[Tuple[Path], Tuple[str]] = (),
                           img_dir: Union[Path, str]) -> None:
        if img_paths and img_dir:
            raise MutualExclusionError('img_paths and img_dir are mutually exclusive'
                                       'only one of these may be provided')

        if not (img_paths or img_dir):
            raise MissingRequiredPathError(
                'img_paths or img_dir must be provided')
