from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List

logger = logging.getLogger(__name__)


class Component(ABC):
    """
    Базовый класс Компонент объявляет общие операции как для простых, так и для
    сложных объектов структуры.
    """

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        """
        При необходимости базовый Компонент может объявить интерфейс для
        установки и получения родителя компонента в древовидной структуре. Он
        также может предоставить некоторую реализацию по умолчанию для этих
        методов.
        """
        self._parent = parent

    """
    В некоторых случаях целесообразно определить операции управления потомками
    прямо в базовом классе Компонент. Таким образом, вам не нужно будет
    предоставлять конкретные классы компонентов клиентскому коду, даже во время
    сборки дерева объектов. Недостаток такого подхода в том, что эти методы
    будут пустыми для компонентов уровня листа.
    """

    def add(self, component: Component) -> None:
        pass

    def remove(self, component: Component) -> None:
        pass

    def is_composite(self) -> bool:
        """
        Вы можете предоставить метод, который позволит клиентскому коду понять,
        может ли компонент иметь вложенные объекты.
        """
        return False

    @abstractmethod
    def operation(self) -> None:
        """
        Базовый Компонент может сам реализовать некоторое поведение по умолчанию
        или поручить это конкретным классам, объявив метод, содержащий поведение
        абстрактным.
        """
        pass


class Leaf(Component):
    """
    Класс Лист представляет собой конечные объекты структуры. Лист не может
    иметь вложенных компонентов.

    Обычно объекты Листьев выполняют фактическую работу, тогда как объекты
    Контейнера лишь делегируют работу своим подкомпонентам.
    """

    def operation(self) -> None:
        pass


class Composite(Component):
    """
    Класс Контейнер содержит сложные компоненты, которые могут иметь вложенные
    компоненты. Обычно объекты Контейнеры делегируют фактическую работу своим
    детям.
    """

    def __init__(self) -> None:
        self._children: List[Component] = []

    """
    Объект контейнера может как добавлять компоненты в свой список вложенных
    компонентов, так и удалять их, как простые, так и сложные.
    """

    def add(self, component: Component) -> None:
        logger.debug(
            "[%s.add(%s)]" % (self.__class__.__name__, component.__class__.__name__)
        )
        self._children.append(component)
        component.parent = self

    def remove(self, component: Component) -> None:
        logger.debug(
            "[%s.remove(%s)]" % (self.__class__.__name__, component.__class__.__name__)
        )
        self._children.remove(component)
        component.parent = None

    def is_composite(self) -> bool:
        logger.debug("[%s.is_composite() result=True]" % self.__class__.__name__)
        return True

    def operation(self) -> None:
        """
        Контейнер выполняет свою основную логику особым образом. Он проходит
        рекурсивно через всех своих детей, собирая и суммируя их результаты.
        Поскольку потомки контейнера передают эти вызовы своим потомкам и так
        далее, в результате обходится всё дерево объектов.
        """
        logger.debug("[%s.operation() started]" % self.__class__.__name__)
        for item in self._children:
            item.operation()
