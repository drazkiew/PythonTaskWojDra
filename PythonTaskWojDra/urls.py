from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Python Task API",
        default_version='v1',
        description="""
        An API to upload, store, resize and retrieve image files.
        
        **Documentation links:**
        - [This site](/swagger)
        - [JSON export of this specification](/swagger.json)
        - [YAML export of this specification](/swagger.yaml)
        - [ReDoc version of this specification](/redoc)
        """,
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = \
    [
        re_path(r'$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-base'),
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
                name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path("", include("apps.images.urls")),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
