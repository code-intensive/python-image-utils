from importlib.machinery import EXTENSION_SUFFIXES
from PIL import Image
from pathlib import Path
from threading import Thread
from exceptions import (
    MutualExclusionError,
    MissingRequiredPathError,
    NotAFileError,
    InvalidImageTypeError
)


SUPPORTED_SUFFIXES = ('png', 'jpg', 'gif')
HOME_DIR = Path.home()


def get_supported_suffixes_as_str() -> str:
    return ', '.join(SUPPORTED_SUFFIXES[:-1]) + ' or ' + SUPPORTED_SUFFIXES[-1]


def validate_image_path(img_path: Path | str) -> bool:
    """
    Carries out basic validation on the image path
    """
    # Validate the image path, type and extension
    if not img_path.exists():
        raise FileNotFoundError(
            '%s was not found in your path, kindly review the path provided' % img_path)
    elif not img_path.is_file():
        raise NotAFileError(
            '%s exists but is not a file, kindly pass a valid file path' % img_path)
    elif not img_path.suffix.lower()[1:] in (SUPPORTED_SUFFIXES):
        raise InvalidImageTypeError(
            'The image file extension is not supported,'
            'supported extensions must be one of the follwing %s' % get_supported_suffixes_as_str())
    return True


def validate_dir_path(img_path: Path | str) -> bool:
    """
    Carries out basic validation on the directory provided
    """
    # Validate the image path, type and extension
    if not(img_path.exists() and img_path.is_dir()):
        return False
    return True


def get_img_paths_from_img_dir(img_dir: Path, extensions: tuple[str] = EXTENSION_SUFFIXES) -> list[Path]:
    """
    Returns a list of image files matching the specified extensions
    within the given directory
    """
    re_group_exts = '|'.join(extensions)
    img_pattern = r'*/*.(%s)' % re_group_exts
    return list(img_dir.glob(img_pattern))


def resize_image(img_path: Path | str, *, extension: str = None, img_height: int = 200, img_width: int = 200) -> bool:
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
    if isinstance(img_path, str):
        img_path = Path(img_path)
    img_path = img_path.resolve()
    # perform basic validation
    if validate_image_path(img_path):
        image = Image.open(img_path)
        # if a new extension is required as output format
        # set the current file's extension type to it
        resized_image = image.resize((img_height, img_width), Image.ANTIALIAS)
        if extension:
            extension = extension.lower() if extension.startswith(
                '.') else '.' + extension.lower()
            img_path = img_path.with_suffix(extension)
        # add a new prefix image file before saving
        resized_image_name = 'resized_%s' % img_path.name
        img_format = img_path.suffix.upper()[1:]
        img_path = img_path.with_name(resized_image_name)
        resized_image.save(img_path, img_format, quality=90)
        print('Resized image was saved at %s in %s format' %
              (img_path, img_format))
        return True
    else:
        return False


def resize_bulk_images(*, img_paths: tuple[Path] | tuple[str] = (), img_dir: Path | str = None,
                       extensions: str = None, img_height: int = 200, img_width: int = 200) -> int:
    """
    Resizes an image file to the new height and width as well as
    a new extension type if extension is provided

    `img_paths`:`tuple[Path]` | `tuple[str]` -> Tuple containing paths of images to be processed

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
    print(img_paths)
    image_paths = img_paths if img_paths else get_img_paths_from_img_dir(
        img_dir, extensions=extensions or EXTENSION_SUFFIXES)

    kwargs = {
        'extension': extensions,
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


dirs = (
    HOME_DIR.joinpath('downloads\WhatsApp Image 2022-04-19 at 10.49.50 PM.jpeg'),
    HOME_DIR.joinpath('downloads\WhatsApp Image 2022-04-20 at 1.11.04 AM.jpeg'),
    HOME_DIR.joinpath('downloads\WhatsApp Image 2022-04-19 at 11.30.44 PM(1).jpeg'),
    HOME_DIR.joinpath('downloads\WhatsApp Image 2022-04-19 at 11.30.44 PM.jpeg'),
    HOME_DIR.joinpath('downloads\WhatsApp Image 2022-04-19 at 11.30.43 PM(1).jpeg')
)

resize_bulk_images(img_paths=dirs)
