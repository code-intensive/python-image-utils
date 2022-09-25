from pathlib import Path
from threading import Thread
from typing import Tuple, Union
from uuid import uuid4

from PIL import Image

from image_utils.config import settings
from image_utils.image_resizer.base import IImageResizer
from image_utils.core.utils import print_if_verbose
from image_utils.validators.base import IValidator


class ImageResizer(IImageResizer):
    def __init__(self, validator: IValidator) -> None:
        self.validator = validator()

    def resize_image(self, img_path: Union[Path, str],
                     *, extension: str = None,
                     img_height: int = 200, img_width: int = 200) -> Path:
        """
        Resizes an image file to the new height and width as well as
        a new extension type if extension is provided

        * `args`:
        `img_path`:`Path` | `str` -> Path to the image file to be processed

        * `kwargs`:
            `extension`:`str` -> Defaults to `None`, If it is provided the
            image's file extension is changed to this type

            `img_height`:`int` -> Defaults to `200`, If provided the image is
            resized to this `height`

            `img_width`:`int` -> Defaults to `200`, If provided the image is
            resized to this `width`

        * `returns` : `bool` -> `True` if the image was resized else `False`
        """
        img_path = self.validator.validate_file(img_path)
        image = Image.open(img_path)

        if hasattr(settings, 'DEFAULT_EXTENSION'):
            extension = settings.DEFAULT_EXTENSION

        resized_image = image.resize(
            (img_width, img_height), Image.ANTIALIAS)

        if extension:
            extension = extension.lower() if extension.startswith(
                '.') else '.' + extension.lower()
            img_path = img_path.with_suffix(extension)

        # add a new prefix image file before saving
        previous_file_name = img_path.name
        resized_image_name = F'resized_{ previous_file_name }'
        img_format = img_path.suffix.upper()[1:]
        img_path = img_path.with_name(resized_image_name)

        if img_path.exists():
            print_if_verbose(F'Duplicate resized image found at { img_path }')

            if not settings.SKIP_EXISTING_FILES:
                print_if_verbose(F'Skipped resizing { img_path.name }\n')
                return img_path

            if not settings.OVERRIDE_EXISTING_FILES:
                uuid_appended_name = '-'.join((img_path.stem, uuid4().hex))
                img_path = img_path.with_stem(uuid_appended_name)
        try:
            resized_image.save(img_path, img_format, quality=90)
        except Exception as e:
            print(F"{e}")
        print_if_verbose(
            F'Resized image - { previous_file_name } ({ img_width }x{ img_height }) (saved at { img_path }) in { img_format } format\n')
        return img_path

    def resize_bulk_images(self, *,
                           img_paths: Union[Tuple[Path], Tuple[str]] = (),
                           img_dir: Union[Path, str] = None, save_as='png',
                           extensions: str = None, img_height: int = 200,
                           img_width: int = 200, recursive: bool = False) -> None:
        """
        Resizes image file to the new height and width as well as
        a new extension type if extension is provided

        `img_paths`:`Tuple[Path]` | `Tuple[str]` -> Tuple containing paths
         or string representation of the image paths to be processed

        `img_dir`:`Path | str` -> Folder containing images to be processed

        `extensions`:`str` -> Defaults to `None`, If it is provided the
        images with file extension type(s) are resized

        `img_height`:`int` -> Defaults to `200`, If provided the image is
        resized to this `height`

        `img_width`:`int` -> Defaults to `200`, If provided the image is
        resized to this `width`

        `returns` : `int` -> Total number of images successfully resized
        """

        self.validator.validate_path_args(img_paths=img_paths, img_dir=img_dir)

        # we use the img_paths argument if it is provided,
        # use the img_dir if the img_paths is not
        image_paths = img_paths or self.get_paths_from_dir(
            img_dir, extensions=extensions or settings.SUPPORTED_EXTENSIONS, recursive=recursive)

        kwargs = {
            'extension': save_as,
            'img_height': img_height,
            'img_width': img_width
        }

        threads: list[Thread] = []
        thread: Thread

        for img_path in image_paths:
            thread = Thread(target=self.resize_image,
                            args=(img_path,), kwargs=kwargs)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
