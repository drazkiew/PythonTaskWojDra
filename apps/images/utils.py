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
    return Response({"error": error}, status=status)


class ImagePreparationError(Exception):
    pass


def prepare_image(image_file: File, width: int, height: int) -> (File, int, int):
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

