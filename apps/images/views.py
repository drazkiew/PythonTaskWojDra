from django.db.models import Q
from django.http import QueryDict
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.images.forms import UploadImageForm
from apps.images.models import Image
from apps.images.serializers import PublicImageSerializer
from apps.images.utils import get_error_response


class ImagesView(APIView):
    def get(self, request: Request) -> Response:
        query = self.create_image_query(request.query_params)
        images = Image.objects.filter(query)
        serializer = PublicImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = UploadImageForm(request.POST, request.FILES)
        if serializer.is_valid():
            try:
                new_obj = Image.create(
                    title=serializer.cleaned_data["title"],
                    width=serializer.cleaned_data["width"],
                    height=serializer.cleaned_data["height"],
                    image=serializer.cleaned_data["image"]
                )
            except Exception as e:
                return get_error_response(str(e), status.HTTP_400_BAD_REQUEST)
            return Response(PublicImageSerializer(new_obj).data, status=status.HTTP_201_CREATED)
        return get_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @classmethod
    def create_image_query(cls, args: QueryDict) -> Q:
        query = Q()
        if "title" in args:
            query &= Q(title__icontains=args["title"])
        return query


class SingleImageView(APIView):
    def get(self, request: Request, image_id: int) -> Response:
        image = Image.objects.filter(pk=image_id).first()
        if image:
            serializer = PublicImageSerializer(image)
            return Response(serializer.data)
        else:
            return get_error_response(f"Image with id.{image_id} not found", status.HTTP_404_NOT_FOUND)
