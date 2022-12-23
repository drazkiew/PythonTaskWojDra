import pytest
from django.urls import reverse
from django.utils.http import urlencode

from .conftest import test_simple_images


@pytest.mark.django_db
def test_images_view_get_empty(api_client):
    url = reverse('images_view')
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'count', [1, 2, 3, 4, 5]
)
def test_images_view_get_list(count, api_client, create_images):
    template_list = test_simple_images[:count]
    create_images(template_list)
    url = reverse('images_view')

    response = api_client.get(url)

    # Check general response data
    assert response.status_code == 200
    assert len(response.data) == count
    # Check if individual results from the list match the templates
    for template in template_list:
        linked = [item for item in response.data if item.get("title") == template.get("title")]
        linked = linked[0] if len(linked) == 1 else None

        assert linked is not None
        assert f"{template['file']}.{template['extension']}" in linked.get("url", "")
        assert linked.get("width") == template["width"]
        assert linked.get("height") == template["height"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'title, expected_count', [
        ('a', 2),
        ('e', 5),
        ('Testing', 1),
        ('Non-existing', 0),
    ]
)
def test_images_view_get_list_title_search(
        title, expected_count, api_client, create_images
):
    create_images(test_simple_images)
    url = reverse('images_view') + '?' + urlencode({'title': title})

    response = api_client.get(url)

    # Check general response data and if the search gave us expected amount of items
    assert response.status_code == 200
    assert len(response.data) == expected_count
