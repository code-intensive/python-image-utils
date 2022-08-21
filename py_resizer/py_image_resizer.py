from pathlib import Path
from threading import Thread
from typing import Tuple, Union, List

from PIL import Image

from exceptions import *


SUPPORTED_SUFFIXES = ('png', 'jpg', 'gif')
HOME_DIR = Path.home()


def get_supported_suffixes_as_str() -> str:
    return ', '.join(SUPPORTED_SUFFIXES[:-1]) + ' or ' + SUPPORTED_SUFFIXES[-1]


def validate_image_path(img_path: Union[Path, str]) -> bool:
    """
    Carries out validation on the image path
    """
    img_path = Path(img_path)
    # Validate the image path, type and extension
    if not img_path.exists():
        raise FileNotFoundError(
            F'{ img_path } was not found in your path, kindly review the path provided')

    if not img_path.is_file():
        raise NotAFileError(
            F'{ img_path } exists but is not a file, kindly pass a valid file path')

    if not img_path.suffix.lower()[1:] in (SUPPORTED_SUFFIXES):
        raise InvalidImageTypeError(
            'The image file extension is not supported, '
            F'supported extensions must be one of the following { get_supported_suffixes_as_str() }')

    return img_path


def validate_dir_path(img_path: Union[Path, str]) -> bool:
    """
    Carries out validation on the directory provided
    """
    img_path = Path(img_path)
    # Validate the image path, type and extension
    if not img_path.exists():
        raise FileNotFoundError(
            F'{ img_path } was not found in your path, kindly review the path provided')

    if not img_path.is_dir():
        raise NotADirectoryError(
            F'{ img_path } exists but is not a directory, kindly pass a valid directory path')

    return img_path


def get_img_paths_from_img_dir(img_dir: Union[Path, str], *, extensions: Tuple[str] = SUPPORTED_SUFFIXES,
                               recursive: bool = False, exit_if_empty: bool = True) -> List[Path]:
    """
    Returns a list of image file paths matching the
    specified extension within the given directory
    """
    img_dir = validate_dir_path(img_dir)
    found_images = []
    search_dir = img_dir.rglob if recursive else img_dir.glob
    start_message = 'Recursively searching for image files at %s' if recursive else 'Searching for image files at %s'
    print(start_message % img_dir)

    for extension in extensions:
        img_pattern = F'*.{ extension }'
        extension = extension.upper()
        found_image = list(search_dir(img_pattern))
        # If we are unable to find any of image of the
        # extension type, we notify the user and continue
        # the loop from the top
        if not found_image:
            print(F'No { extension } image found')
            continue

        found_images.extend(found_image)
        print(F'Found { len(found_image) } { extension } image(s)')

    if not found_images:
        print(F'No image file was found in { img_dir }')
        if exit_if_empty:
            exit(0)
    else:
        print(F'Found { len(found_images) } image(s) at { img_dir }')

    return found_images


def resize_image(img_path: Union[Path, str], *, extension: str = None, img_height: int = 200, img_width: int = 200) -> bool:
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
    img_path = Path(img_path).resolve()

    # perform basic validation
    error_message = None
    try:
        validate_image_path(img_path)
    except InvalidImageTypeError as IET:
        error_message = IET
    except NotAFileError as NAF:
        error_message = NAF
    except FileNotFoundError as FNF:
        error_message = FNF
    else:
        image = Image.open(img_path)
        # if a new extension is required as output format
        # set the current file's extension type to it
        resized_image = image.resize((img_width, img_height), Image.ANTIALIAS)

        if extension:
            extension = extension.lower() if extension.startswith(
                '.') else '.' + extension.lower()
            img_path = img_path.with_suffix(extension)
        # add a new prefix image file before saving
        resized_image_name = F'resized_{ img_path.name }'
        img_format = img_path.suffix.upper()[1:]
        img_path = img_path.with_name(resized_image_name)
        resized_image.save(img_path, img_format, quality=90)
        print(
            F'Resized image to ({ img_width }x{ img_height }) was saved at { img_path } in { img_format } format')
        return True
    print(F'Image resizing failed for {img_path}...\n{error_message},\n')
    return False


def resize_bulk_images(*, img_paths: Union[Tuple[Path], Tuple[str]] = (), img_dir: Union[Path, str] = None, save_as='png',
                       extensions: str = None, img_height: int = 200, img_width: int = 200, recursive: bool = False) -> None:
    """
    Resizes an image file to the new height and width as well as
    a new extension type if extension is provided

    `img_paths`:`Tuple[Path]` | `Tuple[str]` -> Tuple containing paths or string representation of the image paths to be processed

    `img_dir`:`Path | str` -> Folder containing images to be processed

    `extensions`:`str` -> Defaults to `None`, If it is provided the
    images with file extension type(s) are resized

    `img_height`:`int` -> Defaults to `200`, If provided the image is
    resized to this `height`

    `img_width`:`int` -> Defaults to `200`, If provided the image is
    resized to this `width`

    `returns` : `int` -> Total number of images successfully resized
    """

    if img_paths and img_dir:
        raise MutualExclusionError('img_paths and img_dir are mutually exclusive'
                                   'only one of these may be provided')

    if not (img_paths or img_dir):
        raise MissingRequiredPathError('img_paths or img_dir must be provided')

    # we use the img_paths argument if it is provided,
    # use the img_dir if the img_paths is not
    image_paths = img_paths or get_img_paths_from_img_dir(
        img_dir, extensions=extensions or SUPPORTED_SUFFIXES, recursive=recursive)

    kwargs = {
        'extension': save_as,
        'img_height': img_height,
        'img_width': img_width
    }

    threads: list[Thread] = []
    thread: Thread

    for img_path in image_paths:
        thread = Thread(target=resize_image, args=(img_path,), kwargs=kwargs)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
