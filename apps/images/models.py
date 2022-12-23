from django.core.files import File
from django.db import models

from apps.images.utils import prepare_image


class Image(models.Model):
    title = models.CharField(max_length=80)
    width = models.IntegerField()
    height = models.IntegerField()
    image = models.ImageField(upload_to='images')

    @staticmethod
    def create(title: str, width: int, height: int, image: File) -> "Image":
        if not title and image:
            title = str(image.name).split(".")[0]
        image, width, height = prepare_image(image, width, height)
        new_obj = Image.objects.create(
            title=title,
            width=width, height=height,
            image=image
        )
        return new_obj

    @property
    def url(self) -> str:
        return self.image.url

    def __str__(self) -> str:
        return f"Image \"{self.title}\", {self.width}x{self.height}"
