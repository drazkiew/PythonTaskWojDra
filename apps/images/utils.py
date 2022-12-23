from io import BytesIO
from typing import Any

from PIL import Image
from django.core.files import File
from rest_framework.response import Response

image_types = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "bmp": "BMP",
    "gif": "GIF",
    "tif": "TIFF",
    "tiff": "TIFF",
    "webp": "WEBP",
}


def get_error_response(error: Any, status: int) -> Response:
    """
    Function for creating a predictable error response.

    :param error: A JSON-able object, which will be returned within the response
    :param status: HTTP error code
    :return: Error Response
    """
    return Response({"error": error}, status=status)


class ImagePreparationError(Exception):
    pass


def prepare_image(image_file: File, width: int, height: int) -> (File, int, int):
    """
    Function for scaling an image, given as a File, to fit provided size.
    If either width or height are 0, image will be scaled to one of
    the sizes (non-zero one), while keeping its aspect ratio.
    If both are 0, image will not be scaled.

    :param image_file: A file containing an image
    :param width: Intended resulting width of the image
    :param height: Intended resulting height of the image
    :return: Tuple of resulting image file, and its final width and height
    """
    img = Image.open(image_file)
    if width or height:
        if not width:
            width = int(img.width * height / img.height)
        if not height:
            height = int(img.height * width / img.width)
        output_size = (width, height)
        img = img.resize(output_size)
        img_suffix = image_file.name.split(".")[-1].lower()
        if img_suffix not in image_types:
            raise ImagePreparationError(f"File format \"{img_suffix}\" is not supported")
        img_format = image_types[img_suffix]
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        return File(buffer, name=image_file.name), width, height
    return image_file, img.width, img.height

