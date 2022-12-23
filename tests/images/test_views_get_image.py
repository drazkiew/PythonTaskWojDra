import pytest
from django.urls import reverse

from .conftest import test_simple_images


@pytest.mark.django_db
def test_single_image_view_get(api_client, create_images):
    images = create_images(test_simple_images)

    # Fetch all created data via API
    for image in images:
        url = reverse('single_image_view', kwargs={'image_id': image.id})
        response = api_client.get(url)

        # Check if the created object and the data from response match
        assert response.status_code == 200
        assert response.data.get("id") == image.id
        assert response.data.get("title") == image.title
        assert response.data.get("url") == image.url
        assert response.data.get("width") == image.width
        assert response.data.get("height") == image.height


@pytest.mark.django_db
@pytest.mark.parametrize(
    'image_id', [1, 12, 56]
)
def test_single_image_view_get_not_found(image_id, api_client):
    url = reverse('single_image_view', kwargs={'image_id': image_id})
    response = api_client.get(url)

    # Check if error occurred
    assert response.status_code == 404
    assert response.data == {
        "error": f"Image with id.{image_id} not found"
    }
