from pathlib import Path
from typing import Tuple, Union, List
from abc import ABCMeta, abstractmethod

from image_utils.config import settings
from image_utils.core.utils import print_if_verbose
from image_utils.validators.base import IValidator


class IImageResizer(metaclass=ABCMeta):
    """ Abstract base class for all Image resizer classes"""

    def __init__(self, validator: IValidator) -> None:
        self.validator: IValidator = validator()

    def get_paths_from_dir(self,
                           dir: Union[Path, str], *,
                           extensions: Tuple[str] = settings.SUPPORTED_EXTENSIONS,
                           recursive: bool = False,
                           exit_if_empty: bool = True) -> List[Path]:
        """

        Returns a list of file paths matching the
        specified extension within the given directory

        """

        dir = self.validator.validate_directory(dir)
        found_files = []
        search_dir = dir.rglob if recursive else dir.glob
        start_message = 'Recursively searching for image files at %s' if recursive else 'Searching for image files at %s'
        print_if_verbose(start_message % dir)

        for extension in extensions:
            file_pattern = F'*.{ extension }'
            extension = extension.upper()
            found_image = list(search_dir(file_pattern))
            # If we are unable to find any of file of the
            # extension type, we notify the user and continue
            # the loop from the top
            if not found_image:
                print_if_verbose(F'No { extension } image found')
                continue

            found_files.extend(found_image)
            print_if_verbose(
                F'Found { len(found_image) } { extension } image(s)')

        if not found_files:
            print_if_verbose(F'No file was found in { dir }')
            if exit_if_empty:
                exit(0)
        else:
            print_if_verbose(F'Found { len(found_files) } image(s) at { dir }')

        return found_files

    @abstractmethod
    def resize_image(self, img_path: Union[Path, str],
                     *, extension: str = None,
                     img_height: int = 200, img_width: int = 200) -> bool:
        ...

    @abstractmethod
    def resize_bulk_images(self, *,
                           img_paths: Union[Tuple[Path], Tuple[str]] = (),
                           img_dir: Union[Path, str] = None, save_as='png',
                           extensions: str = None, img_height: int = 200,
                           img_width: int = 200, recursive: bool = False) -> None:
        ...
