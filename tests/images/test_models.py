import os

import pytest
from django.core.files import File

from apps.images.models import Image
from PIL import Image as PillowImage

from .conftest import test_simple_images


@pytest.mark.django_db
@pytest.mark.parametrize(
    'title, width, height, file, extension, file_format', [
        ("example", 300, 200, "example", "png", "PNG"),
        ("another", 120, 52, "another", "gif", "GIF"),
        ("hello?", 576, 1224, "hello", "jpg", "JPEG"),
        ("Testing", 231, 201, "testing", "tiff", "TIFF"),
        ("New one", 256, 512, "new_one", "webp", "WEBP"),
    ]
)
def test_image_create(
        title, width, height, file, extension, file_format,
        create_image_file, remove_images_afterwards
):
    filename = f"{file}.{extension}"
    create_image_file(filename, file_format, width, height)
    with open(filename, "rb") as test_file:
        created = Image.create(
            title, width, height, File(test_file)
        )
    os.remove(filename)

    comparison = Image.objects.get(id=created.id)
    saved_image = PillowImage.open(comparison.image.path) if comparison else None

    # Check if created object's data matches expected values
    assert created
    assert created.title == title
    assert created.width == width
    assert created.height == height
    assert filename in created.url

    # Check if saved image's parameters are as expected
    assert saved_image
    assert saved_image.width == width
    assert saved_image.height == height


@pytest.mark.django_db
@pytest.mark.parametrize(
    'file, extension, file_format', [
        ("example", "png", "PNG"),
        ("another", "gif", "GIF"),
    ]
)
def test_image_create_same_filename(
        file, extension, file_format,
        create_image_file, remove_images_afterwards
):
    filename = f"{file}.{extension}"
    create_image_file(filename, file_format, 100, 100)
    with open(filename, "rb") as test_file:
        first_created = Image.create(
            "test1", 100, 100, File(test_file)
        )
        second_created = Image.create(
            "test2", 100, 100, File(test_file)
        )
        third_created = Image.create(
            "test3", 100, 100, File(test_file)
        )
    os.remove(filename)

    # check if all the file names are different
    assert first_created
    assert second_created
    assert not first_created.image.name == second_created.image.name
    assert not first_created.image.name == third_created.image.name
    assert not second_created.image.name == third_created.image.name


@pytest.mark.django_db
def test_image_url(create_images):
    images = create_images(test_simple_images)

    # Check if all image objects' url parameter matches its intended value
    for image in images:
        assert image
        assert image.url == image.image.url


@pytest.mark.django_db
def test_image_str(create_images):
    images = create_images(test_simple_images)

    # Check if all image objects' string value matches its intended value
    for image in images:
        assert image
        assert str(image) == f"Image \"{image.title}\", {image.width}x{image.height}"
