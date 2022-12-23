import os

import pytest
from django.core.files import File

from apps.images.models import Image
from PIL import Image as PillowImage

from .conftest import test_simple_images


@pytest.mark.django_db
@pytest.mark.parametrize(
    'title, width, height, file, extension, format', [
        ("example", 300, 200, "example", "png", "PNG"),
        ("another", 120, 52, "another", "gif", "GIF"),
        ("hello?", 576, 1224, "hello", "jpg", "JPEG"),
        ("Testing", 231, 201, "testing", "tiff", "TIFF"),
        ("New one", 256, 512, "new_one", "webp", "WEBP"),
    ]
)
def test_image_create(
        title, width, height, file, extension, format,
        create_image_file, remove_images_afterwards
):
    filename = f"{file}.{extension}"
    image_size = create_image_file(filename, format, width, height)
    with open(filename, "rb") as test_file:
        created = Image.create(
            title, width, height, File(test_file)
        )
    os.remove(filename)

    comparison = Image.objects.get(id=created.id)
    saved_image = PillowImage.open(comparison.image.path) if comparison else None

    assert created
    assert created.title == title
    assert created.width == width
    assert created.height == height
    assert filename in created.url

    assert saved_image
    assert saved_image.width == width
    assert saved_image.height == height
    assert saved_image.size == image_size


@pytest.mark.django_db
def test_image_url(create_images):
    images = create_images(test_simple_images)

    for image in images:
        assert image
        assert image.url == image.image.url


@pytest.mark.django_db
def test_image_str(create_images):
    images = create_images(test_simple_images)

    for image in images:
        assert image
        assert str(image) == f"Image \"{image.title}\", {image.width}x{image.height}"
