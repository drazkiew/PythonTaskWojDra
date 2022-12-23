import os

import pytest
from django.core.files import File
from PIL import Image as PillowImage

from apps.images.utils import get_error_response, prepare_image, ImagePreparationError


@pytest.mark.parametrize(
    'error, status', [
        ("Test error!", 400),
        ({"test": "dict"}, 401),
        (["test", "list"], 402),
        (None, 403),
    ]
)
def test_get_error_response(error, status):
    response = get_error_response(error, status)

    # Check if created response matches its expected properties
    assert response.status_code == status
    assert response.data == {"error": error}


@pytest.mark.parametrize(
    'filename, file_format, width, height, resize_width, resize_height', [
        ("test.png", "PNG", 400, 300, 400, 300),
        ("test.gif", "GIF", 400, 300, 323, 120),
        ("test.tiff", "TIFF", 400, 300, 543, 443),
        ("test.bmp", "BMP", 400, 300, 0, 400),
        ("test.jpg", "JPEG", 400, 300, 0, 220),
        ("test.jpeg", "JPEG", 400, 300, 560, 0),
        ("test.webp", "WEBP", 400, 300, 200, 0),
    ]
)
def test_prepare_image(
        filename, file_format, width, height, resize_width, resize_height,
        create_image_file
):
    create_image_file(filename, file_format, width, height)
    with open(filename, "rb") as file_binary:
        result_file, result_width, result_height = prepare_image(
            File(file_binary, name=filename), resize_width, resize_height
        )
    os.remove(filename)

    if resize_width or resize_height:
        resize_width = int(width * resize_height / height) \
            if not resize_width else resize_width
        resize_height = int(height * resize_width / width) \
            if not resize_height else resize_height
    else:
        resize_width = width
        resize_height = height

    result_image = PillowImage.open(result_file)

    # Check if the resulting image matches provided parameters
    assert result_file
    assert result_image
    assert result_image.width == resize_width
    assert result_image.height == resize_height

    assert result_width == resize_width
    assert result_height == resize_height


@pytest.mark.parametrize(
    'filename, file_format, width, height', [
        ("test.jpeg", "JPEG", 436, 443),
        ("test.webp", "WEBP", 400, 300),
    ]
)
def test_prepare_image_no_resize(
        filename, file_format, width, height,
        create_image_file
):
    create_image_file(filename, file_format, width, height)
    with open(filename, "rb") as file_binary:
        file = File(file_binary, name=filename)
        result_file, result_width, result_height = prepare_image(
            file, 0, 0
        )

        # Check if file is the same
        assert result_file
        assert file
        assert file == result_file
        assert result_width == width
        assert result_height == height
    os.remove(filename)


@pytest.mark.parametrize(
    'extension, file_format', [
        ("ico", "ICO"),
        ("eps", "EPS"),
    ]
)
def test_prepare_image_not_supported_format(
        extension, file_format,
        create_image_file
):
    filename = f"test.{extension}"
    create_image_file(filename, file_format, 100, 100)

    # Check if exception is thrown
    with open(filename, "rb") as file_binary:
        file = File(file_binary, name=filename)
        try:
            prepare_image(file, 100, 100)
            assert False
        except ImagePreparationError as e:
            assert str(e) == f"File format \"{extension}\" is not supported"
    os.remove(filename)
