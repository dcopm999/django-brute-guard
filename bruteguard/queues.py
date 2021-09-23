from abc import ABC, abstractmethod
from typing import List

from django.core.cache import caches


class BaseManager(ABC):
    @abstractmethod
    def input_get(self, key):
        """
        Абстрактный метод для получения из входной очереди значение по ключу
        """
        pass

    @abstractmethod
    def input_set(self, key, value):
        pass

    @abstractmethod
    def input_remove(self, key):
        pass

    @abstractmethod
    def output_get(self, key):
        pass

    @abstractmethod
    def output_set(self, key, value):
        pass

    @abstractmethod
    def output_remove(self, key):
        pass

    @abstractmethod
    def input_keys(self):
        pass

    @abstractmethod
    def output_keys(self):
        pass


class DjangoCacheManager(BaseManager):
    CACHE_NAME = "bruteguard"

    def __init__(self):
        self._input_queue = caches[self.CACHE_NAME]
        self._output_queue = self._input_queue
        super().__init__()

    def input_get(self, key: str) -> str:
        assert isinstance(key, str)
        return self._input_queue.get(key)

    def input_set(self, key: str, value: str) -> bool:
        assert isinstance(key, str)
        assert isinstance(value, str)
        return self._input_queue.set(key, value)

    def input_remove(self, key: str) -> bool:
        assert isinstance(key, str)
        return self._input_queue.delete(key)

    def output_get(self, key: str) -> str:
        assert isinstance(key, str)
        return self._output_queue.get(key)

    def output_set(self, key: str, value: str) -> bool:
        assert isinstance(key, str)
        assert isinstance(value, str)
        return self._output_queue.get(key)

    def output_remove(self, key: str) -> bool:
        assert isinstance(key, str)
        return self._output_queue.get(key)

    def input_keys(self) -> List[str]:
        return self._input_queue.keys("*")

    def output_keys(self) -> List[str]:
        return self._output_queue.keys("*")
