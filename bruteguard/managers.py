import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from bruteguard import validators
from bruteguard.patterns.composite import Composite
from bruteguard.queues import BaseQueue, DjangoCacheQueue, SingletonQueue

logger = logging.getLogger(__name__)


class BaseManager(Composite):
    QUEUE = BaseQueue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.QUEUE = self.QUEUE()

        try:
            VALIDATORS = [
                getattr(validators, item)
                for item in settings.BRUTE_GUARD.get("VALIDATORS")
            ]
        except TypeError:
            VALIDATORS = []

        for validator in VALIDATORS:
            self.add(validator())

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
