from pathlib import Path
from typing import Tuple, Union
from abc import ABCMeta, abstractmethod


class IValidator(metaclass=ABCMeta):
    @abstractmethod
    def validate_path(self, path: Union[Path, str]) -> Path:
        """ Validates the existence of the provided path """
        ...

    @abstractmethod
    def validate_file_extensions(self, file_: Path) -> None:
        ...

    @abstractmethod
    def validate_file(self, path: Union[Path, str]) -> Path:
        """ Carries out validation on the file provided """
        ...

    @abstractmethod
    def validate_directory(self, path: Union[Path, str]) -> Path:
        """ Carries out validation on the directory provided """
        ...

    @abstractmethod
    def validate_path_args(self, *,
                           img_paths: Union[Tuple[Path], Tuple[str]] = (),
                           img_dir: Union[Path, str]) -> None:
        ...
