import pytest
from PIL import Image as PillowImage
from django.urls import reverse

from apps.images.models import Image


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
def test_images_view_post(
        title, width, height, file, extension, format,
        api_client, post_image, create_image_file, remove_images_afterwards
):
    filename = f"{file}.{extension}"

    image_size = create_image_file(filename, format, width, height)
    response = post_image(api_client, title, filename, width, height)

    # open uploaded file
    created = Image.objects.get(id=response.data.get("id"))
    saved_image = PillowImage.open(created.image.path) if created else None

    # Check general response data
    assert response.status_code == 201
    assert response.data.get("id")
    assert response.data.get("title") == title
    assert response.data.get("width") == width
    assert response.data.get("height") == height
    assert filename in response.data.get("url")

    # Check if saved file is the same
    assert saved_image
    assert saved_image.width == width
    assert saved_image.height == height
    assert saved_image.format == format
    assert saved_image.size == image_size


@pytest.mark.django_db
@pytest.mark.parametrize(
    'width, height, resize_width, resize_height', [
        (300, 200, 200, 100),
        (300, 200, 600, 400),
        (576, 1224, 320, 0),
        (576, 1224, 785, 0),
        (231, 201, 0, 100),
        (231, 201, 0, 540),
        (256, 512, 0, 0)
    ]
)
def test_images_view_post_resize(
        width, height, resize_width, resize_height,
        api_client, post_image, create_image_file, remove_images_afterwards
):
    filename = "test.png"

    create_image_file(filename, "PNG", width, height)
    response = post_image(api_client, "test", filename, resize_width, resize_height)

    # open uploaded file
    created = Image.objects.get(id=response.data.get("id"))
    saved_image = PillowImage.open(created.image.path) if created else None

    # Set resize variables to expected sizes after uploading
    if resize_width or resize_height:
        resize_width = int(width * resize_height / height) \
            if not resize_width else resize_width
        resize_height = int(height * resize_width / width) \
            if not resize_height else resize_height
    else:
        resize_width = width
        resize_height = height

    # Check general response data
    assert response.status_code == 201
    assert response.data.get("width") == resize_width
    assert response.data.get("height") == resize_height

    # Check if saved file is resized properly
    assert saved_image
    assert saved_image.width == resize_width
    assert saved_image.height == resize_height


@pytest.mark.django_db
@pytest.mark.parametrize(
    'file, extension', [
        ("example", "png"),
        ("another", "gif"),
    ]
)
def test_images_view_post_no_title(
        file, extension,
        api_client, post_image, create_image_file, remove_images_afterwards
):
    filename = f"{file}.{extension}"

    create_image_file(filename, "PNG", 100, 100)
    response = post_image(api_client, None, filename, 100, 100)

    # Check general response data
    assert response.status_code == 201
    assert response.data.get("title") == file


@pytest.mark.django_db
def test_images_view_post_no_image(
        api_client, post_image, create_image_file, remove_images_afterwards
):
    url = reverse('images_view')

    post_data = {
        "title": "test",
        "width": 100,
        "height": 100,
    }
    response = api_client.post(
        url, post_data, format="multipart"
    )

    # Check if error occurred
    assert response.status_code == 400
    assert response.data == {'error': {'image': ['This field is required.']}}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'width, height, expected_error', [
        (
                -1, 100,
                {'error': {'width': ['Ensure this value is greater than or equal to 0.']}}
        ),
        (
                100, -12,
                {'error': {'height': ['Ensure this value is greater than or equal to 0.']}}
        ),
        (
                -23, -3444,
                {'error': {'width': ['Ensure this value is greater than or equal to 0.'],
                           'height': ['Ensure this value is greater than or equal to 0.']}}
        ),
    ]
)
def test_images_view_post_negative_numbers(
        width, height, expected_error,
        api_client, post_image, create_image_file, remove_images_afterwards
):
    create_image_file("test.png", "PNG", abs(width), abs(height))
    response = post_image(api_client, "test", "test.png", width, height)

    # Check general response data
    assert response.status_code == 400
    assert response.data == expected_error


@pytest.mark.django_db
@pytest.mark.parametrize(
    'extension, file_format', [
        ('ico', 'ICO'),
        ('eps', 'EPS')
    ]
)
def test_images_view_post_unsupported_format(
        extension, file_format,
        api_client, post_image, create_image_file, remove_images_afterwards
):
    create_image_file(f"test.{extension}", file_format, 100, 100)
    response = post_image(api_client, "test", f"test.{extension}", 100, 100)

    # Check general response data
    assert response.status_code == 400
    assert response.data == {'error': f'File format "{extension}" is not supported'}