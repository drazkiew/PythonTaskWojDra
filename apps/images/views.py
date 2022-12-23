from django.db.models import Q
from django.http import QueryDict
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.images.forms import UploadImageForm
from apps.images.models import Image
from apps.images.serializers import PublicImageSerializer
from apps.images.utils import get_error_response


class ImagesView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary="Returns a list of image objects",
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_QUERY,
                description="Returns images, whose \"title\" contains this value",
                type=openapi.TYPE_STRING
            )
        ], responses={
            200: openapi.Response('response description', PublicImageSerializer)
        },
        security=[]
    )
    def get(self, request: Request) -> Response:
        """
        API Endpoint for retrieving list of image objects.

        URL Query parameter:
        - **title** - (*optional*) If provided, will filter out objects, whose "title" property
        does not contain provided text (case-insensitive).
        """
        query = self.create_image_query(request.query_params)
        images = Image.objects.filter(query)
        serializer = PublicImageSerializer(images, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Upload image",
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_FORM, description="Image's title", type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'width', openapi.IN_FORM, description="Image's final width. Must be >= 0", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'height', openapi.IN_FORM, description="Image's final height. Must be >= 0", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'image', openapi.IN_FORM, description="Image's file", type=openapi.TYPE_FILE, required=True
            )
        ],
        responses={
            200: openapi.Response('response description', PublicImageSerializer)
        },
        security=[]
    )
    def post(self, request: Request) -> Response:
        """
        API Endpoint for uploading and resizing images.

        Form data parameters:
        - **title** - (*optional*) Image's title. If left empty, or excluded,
        image's filename will be taken as "title" instead.
        - **width** and **height** - (*optional*) They describe image's final size.
            - If both variables are included, the image will be scaled match that size.
            - If one of them is excluded or equal to 0, the image will be scaled
            to match the provided size, while keeping original aspect ratio.
            - If both are not provided or are equal to 0, the image's size will be left intact.
        - **image** - (*required*) Image's file. If a file with exactly the same name exists already
        on the server, a suffix will be added to differentiate them.
        """
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
    @swagger_auto_schema(
        operation_summary="Get image object",
        responses={
            200: openapi.Response('response description', PublicImageSerializer)
        },
        security=[]
    )
    def get(self, request: Request, image_id: int) -> Response:
        """
        API Endpoint for retrieving a single image object.

        URL parameter:
        - **image_id** - (*required*) Image object's id.
        """
        image = Image.objects.filter(pk=image_id).first()
        if image:
            serializer = PublicImageSerializer(image)
            return Response(serializer.data)
        else:
            return get_error_response(f"Image with id.{image_id} not found", status.HTTP_404_NOT_FOUND)
