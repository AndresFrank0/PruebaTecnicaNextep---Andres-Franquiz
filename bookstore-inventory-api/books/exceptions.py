import logging

from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def json_exception_handler(exc, context):
    """Manejador de errores de la API (REST_FRAMEWORK['EXCEPTION_HANDLER'])."""
    if isinstance(exc, Http404):
        # Django fija su mensaje en inglés ("No Book matches the given query."); DRF lo traduce.
        exc = NotFound()
    response = exception_handler(exc, context)
    if response is None:
        # Error no controlado: se registra con su traceback y el cliente recibe un 500 en JSON,
        # no la página HTML de Django.
        logger.error('Unhandled API error', exc_info=exc)
        response = Response({'detail': 'Error interno del servidor.'}, status=500)
    return response
