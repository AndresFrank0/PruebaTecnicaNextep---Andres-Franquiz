from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.views import exception_handler


def json_exception_handler(exc, context):
    """Manejador de errores de la API (REST_FRAMEWORK['EXCEPTION_HANDLER'])."""
    if isinstance(exc, Http404):
        # Django fija su mensaje en inglés ("No Book matches the given query."); DRF lo traduce.
        exc = NotFound()
    return exception_handler(exc, context)
