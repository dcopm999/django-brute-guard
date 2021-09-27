import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from bruteguard import managers

logger = logging.getLogger(__name__)


def brute_guard(get_response):
    logger.debug("[%s.brute_guard] activated" % __name__)
    try:
        manager = settings.BRUTE_GUARD.get("MANAGER")
    except AttributeError:
        manager = None
    finally:
        manager = (
            getattr(managers, manager)
            if manager is not None
            else getattr(managers, "DjangoCacheManager")
        )
        manager = manager()

    def middleware(request: HttpRequest) -> HttpResponse:
        logger.debug("[%s.brute_guard] request verification" % __name__)
        assert isinstance(request, HttpRequest)
        response = get_response(request)
        if isinstance(response, HttpResponse):
            manager.operation(request, response)
        return response

    return middleware
