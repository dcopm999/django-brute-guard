import datetime
import logging
from typing import Dict

from django.http import HttpRequest, HttpResponse

from bruteguard.patterns.composite import Composite, Leaf
from bruteguard.queues import BaseQueue, DjangoCacheQueue, SingletonQueue

logger = logging.getLogger(__name__)


class HistoryUpdateLeaf(Leaf):
    def get_request_body(self, request) -> Dict[str, str]:
        assert isinstance(request, HttpRequest)

        body = request.body.decode()
        result: Dict[str, str] = dict(
            item.split("=") for item in body.split("&") if len(body)
        )
        if len(result):
            result["datetime"] = str(datetime.datetime.now())
        return result

    def operation(self, request, response):
        logger.debug("[%s.operation() started]" % self.__class__.__name__)
        assert isinstance(request, HttpRequest)
        assert isinstance(response, HttpResponse)

        if hasattr(response, "context_data") and not response.context_data.get(
            "has_permission"
        ):
            REMOTE_ADDR = request.META["REMOTE_ADDR"]
            REQUEST_BODY = self.get_request_body(request)
            PATH_INFO = request.META["PATH_INFO"]
            KEY = f"{REMOTE_ADDR}:{PATH_INFO}"

            logger.debug(
                "[%s.operation()]: request not authenticated" % self.__class__.__name__
            )
            logger.debug(
                "[%s.operation()]: PATH_INFO = %s"
                % (self.__class__.__name__, PATH_INFO)
            )
            logger.debug(
                "[%s.operation()]: REMOTE_ADDR = %s"
                % (self.__class__.__name__, REMOTE_ADDR)
            )
            logger.debug(
                "[%s.operation()]: REQUEST_BODY = %s"
                % (self.__class__.__name__, REQUEST_BODY)
            )
            logger.debug("[%s.operation()]: KEY = %s" % (self.__class__.__name__, KEY))

            if len(REQUEST_BODY):
                if self.parent.QUEUE.has_key(KEY):  # noqa
                    result = self.parent.QUEUE.get(KEY)
                    result.append(REQUEST_BODY)
                else:
                    result = [REQUEST_BODY]
                self.parent.QUEUE.set(KEY, result)
        logger.debug("[%s.operation() ended]" % self.__class__.__name__)


class BaseManager(Composite):
    QUEUE = BaseQueue

    def __init__(self, *args, **kwargs):
        self.QUEUE = self.QUEUE()
        super().__init__(*args, **kwargs)

    def operation(self, request, response):
        logger.debug("[%s.operation() started]" % self.__class__.__name__)
        assert isinstance(request, HttpRequest)
        assert isinstance(response, HttpResponse)
        for item in self._children:
            item.operation(request, response)
        logger.debug("[%s.operation() ended]" % self.__class__.__name__)


class DjangoCacheManager(BaseManager):
    QUEUE = DjangoCacheQueue


class SingletonManager(BaseManager):
    QUEUE = SingletonQueue
