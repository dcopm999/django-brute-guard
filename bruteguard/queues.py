import logging
from abc import ABC, abstractmethod
from typing import Dict, List

from django.core.cache import caches

from bruteguard.patterns.singleton import Singleton

logger = logging.getLogger(__name__)


class BaseQueue(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def remove(self, key):
        pass

    @abstractmethod
    def has_key(self, key):
        pass


class DjangoCacheQueue(BaseQueue):
    CACHE_NAME = "default"  # settings.CACHES backend name

    def __init__(self, *args, **kwargs):
        self._queue = caches[self.CACHE_NAME]
        logger.debug(
            "[%s.__init__()] using settings.CACHES[%s]"
            % (self.__class__.__name__, self.CACHE_NAME)
        )
        logger.debug(
            "[%s.__init__()] self._queue type %s[%s]"
            % (self.__class__.__name__, self._queue.__class__.__name__, self.CACHE_NAME)
        )
        super().__init__(*args, **kwargs)

    def get(self, key: str) -> List[Dict]:
        assert isinstance(key, str)
        result = self._queue.get(key)
        logger.debug(
            "[%s.get(key)]: key=%s, result=%s" % (self.__class__.__name__, key, result)
        )
        return result

    def set(self, key: str, value: List[Dict]) -> bool:
        assert isinstance(key, str)
        assert isinstance(value, list)
        result = self._queue.set(key, value)
        logger.debug(
            "[%s.set(key)]: key=%s, result=%s" % (self.__class__.__name__, key, result)
        )
        return result

    def remove(self, key: str) -> bool:
        assert isinstance(key, str)
        result = self._queue.delete(key)
        logger.debug(
            "[%s.remove(key)]: key=%s, result=%s"
            % (self.__class__.__name__, key, result)
        )
        return result

    def has_key(self, key) -> bool:
        assert isinstance(key, str)
        result = key in self._queue
        logger.debug(
            "[%s.has_key(key)]: key=%s, result=%s"
            % (self.__class__.__name__, key, result)
        )
        return result


class SingletonQueue(BaseQueue, Singleton):
    def __init__(self, *args, **kwargs):
        self._queue: Dict[str, str] = {}
        super().__init__(*args, **kwargs)

    def get(self, key: str):
        assert isinstance(key, str)
        logger.debug(
            "[%s.get(key)]: key=%s, result=%s"
            % (self.__class__.__name__, key, self._queue.get(key))
        )
        return self._queue.get(key)

    def set(self, key, value):
        assert isinstance(key, str)
        assert isinstance(value, list)
        self._queue[key] = value
        logger.debug(
            "[%s.set(key)]: key=%s, result=%s"
            % (self.__class__.__name__, key, self._queue[key])
        )
        return True

    def remove(self, key):
        assert isinstance(key, str)
        del self._queue[key]
        logger.debug(
            "[%s.remove(key)]: key=%s, result=%s"
            % (self.__class__.__name__, key, self._queue)
        )
        return True

    def has_key(self, key):
        return key in self._queue.keys()
