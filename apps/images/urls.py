from django.urls import path

from apps.images.views import ImagesView, SingleImageView

urlpatterns = [
    path("images/", ImagesView.as_view(), name="images_view"),
    path("images/<int:image_id>", SingleImageView.as_view(), name="single_image_view"),
]
