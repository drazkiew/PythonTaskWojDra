from rest_framework import serializers

from apps.images.models import Image


class PublicImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            "id", "url", "title", "width", "height"
        ]
