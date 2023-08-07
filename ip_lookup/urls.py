from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="IP Lookup API",
        default_version="v1",
        description="API documentation",
    ),
    public=True,  # maybe not the best idea
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path("v1/", include("api.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

urlpatterns += staticfiles_urlpatterns()
