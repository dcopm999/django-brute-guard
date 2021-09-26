import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from bruteguard import managers

logger = logging.getLogger(__name__)


def brute_guard(get_response):
    logger.debug("[%s.brute_guard] activated" % __name__)
    manager = getattr(
        managers, settings.BRUTE_GUARD.get("MANAGER", "DjangoCacheManager")
    )
    manager = manager()

    def middleware(request: HttpRequest) -> HttpResponse:
        logger.debug("[%s.brute_guard] request verification" % __name__)
        assert isinstance(request, HttpRequest)
        response: HttpResponse = get_response(request)
        manager.operation(request, response)
        return response

    return middleware
