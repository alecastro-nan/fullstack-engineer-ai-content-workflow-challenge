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
    # csrf_exempt is safe here: this is a JSON-only GraphQL endpoint using
    # Bearer token auth (no cookies). Content-Type validation in
    # AuthGraphQLView.dispatch() rejects non-application/json POST requests.
    path("graphql", csrf_exempt(AuthGraphQLView.as_view(schema=schema))),  # type: ignore[arg-type]
)
