import os
from io import BytesIO
from typing import List

import pytest
from PIL import Image as PillowImage
from django.core.files import File
from django.urls import reverse

from apps.images.models import Image

test_simple_images = [
    {
        "title": "example", "file": "example",
        "extension": "png", "format": "PNG", "width": 300, "height": 200
    },
    {
        "title": "another", "file": "another",
        "extension": "gif", "format": "GIF", "width": 120, "height": 52
    },
    {
        "title": "hello?", "file": "hello",
        "extension": "jpg", "format": "JPEG", "width": 576, "height": 1224
    },
    {
        "title": "Testing", "file": "testing",
        "extension": "tiff", "format": "TIFF", "width": 231, "height": 201
    },
    {
        "title": "New one", "file": "new_one",
        "extension": "webp", "format": "WEBP", "width": 256, "height": 512
    },
]


@pytest.fixture()
def create_images():
    def inner_create_images(image_templates: List[dict]):
        image_list = []
        for template in image_templates:
            img = PillowImage.new(
                'RGB', (template["width"], template["height"]),
                color='red'
            )
            buffer = BytesIO()
            img.save(buffer, format=template.get('format', 'PNG'))
            image_list.append(Image.objects.create(
                title=template["title"],
                width=template["width"], height=template["height"],
                image=File(
                    buffer,
                    name=f"{template['file']}.{template.get('extension', 'png')}"
                )
            ))
        return image_list

    yield inner_create_images

    for image in Image.objects.all():
        if os.path.exists(image.image.path):
            os.remove(image.image.path)


@pytest.fixture()
def remove_images_afterwards():
    yield

    for image in Image.objects.all():
        if os.path.exists(image.image.path):
            os.remove(image.image.path)


@pytest.fixture()
def create_image_file():
    def inner_create_images(filename: str, file_format: str, width: int, height: int):
        img = PillowImage.new(
            'RGB', (width, height),
            color='red'
        )
        img.save(filename, format=file_format)
        return img.size

    yield inner_create_images


@pytest.fixture()
def post_image():
    from rest_framework.test import APIClient

    def inner_post_image(
            api_client: APIClient, title: str,
            filename: str, width: int, height: int
    ):
        url = reverse('images_view')

        with open(filename, "rb") as test_file:
            post_data = {
                "width": width,
                "height": height,
                "image": test_file
            }
            if title:
                post_data["title"] = title
            response = api_client.post(
                url, post_data, format="multipart"
            )
        os.remove(filename)
        return response

    yield inner_post_image
