from importlib.machinery import EXTENSION_SUFFIXES
from PIL import Image
from pathlib import Path
from threading import Thread
from .exceptions import (
    MutualExclusionError,
    MissingRequiredPathError
)


IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')
HOME_DIR = Path.home()


def validate_image_path(img_path: Path | str) -> bool:
    """
    Carries out basic validation on the image path
    """
    # Validate the image path, type and extension
    if not(img_path.exists() and img_path.is_file() and img_path.suffix in (IMAGE_EXTENSIONS)):
        return False
    return True


def validate_dir_path(img_path: Path | str) -> bool:
    """
    Carries out basic validation on the directory provided
    """
    # Validate the image path, type and extension
    if not(img_path.exists() and img_path.is_dir()):
        return False
    return True

def get_img_paths_from_img_dir(img_dir:Path, extensions:tuple(str)=EXTENSION_SUFFIXES) -> list[Path]:
    pass

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
        img_path = Path(str)
    img_path = img_path.resolve()
    # perform basic validation
    if validate_image_path(img_path):
        image = Image.open(img_path)
        # if a new extension is required as output format
        # set the current file's extension type to it
        if extension:
            img_path.suffix = img_path.with_suffix(extension.lower())
        resized_image = image.resize((img_height, img_width), Image.ANTIALIAS)
        # add a new prefix image file before saving
        resized_image_name = 'resized_%s' % img_path.name
        resized_image.save(img_path.with_name(resized_image_name),
                           img_path.suffix.upper(), quality=90)
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
    image_paths = img_paths if img_paths else get_img_paths_from_img_dir(img_dir, extensions=extensions or EXTENSION_SUFFIXES)
    args = (image_path,)
    kwargs = {
        'extension':extensions,
        'img_height':img_height,
        'img_width':img_width
    }
    
    threads:list[Thread] = []
    thread:Thread
    
    for image_path in image_paths:
        thread = Thread(target=resize_image, *args, **kwargs)
        thread.start()
        threads.append(thread)
        
    for thread in threads:
        thread.join()
