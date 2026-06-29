from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from apps.auth.views import AuthGraphQLView
from config.schema import schema

urlpatterns = []

if settings.DEBUG:
    urlpatterns.append(path("admin/", admin.site.urls))

urlpatterns.append(
    path("graphql", csrf_exempt(AuthGraphQLView.as_view(schema=schema))),  # type: ignore[arg-type]
)
