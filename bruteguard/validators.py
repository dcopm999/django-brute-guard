import datetime
import logging
from typing import Dict

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from bruteguard import models
from bruteguard.patterns.composite import Leaf

logger = logging.getLogger(__name__)


class BruteForceValidator(Leaf):
    def __init__(self):
        super().__init__()
        self._OPTIONS = settings.BRUTE_GUARD.get("OPTIONS")
        if self._OPTIONS is None:
            self._OPTIONS = {
                "error_attempts_counter": 5,
                "base_blocking_rate_minutes": 1,
                "multiple_blocking_rate": False,
            }

    def get_request_body(self, request) -> Dict[str, str]:
        """
        method for gettering payload from request as dict
        """
        assert isinstance(request, HttpRequest)
        body = request.body.decode()
        result: Dict[str, str] = dict(
            item.split("=") for item in body.split("&") if len(body)
        )
        if len(result):
            result["datetime"] = str(timezone.now())
        logger.debug(
            "[%s.get_request_body()]: result=%s" % (self.__class__.__name__, result)
        )
        return result

    def until_verify(self, request) -> None:
        """
        method for matching remote host in blocking list
        """
        assert isinstance(request, HttpRequest)
        REMOTE_ADDR = request.META["REMOTE_ADDR"]
        # если ip удаленного хоста находится в списке блокировки
        if models.Blocked.host_is_blocked(REMOTE_ADDR):
            logger.info(
                "[%s.until_verify()]: REMOTE_ADDR: %s is blocked"
                % (self.__class__.__name__, REMOTE_ADDR)
            )
            # если settings.BRUTE_GUARD.OPETIONS["multiple_blocking_rate"] = True
            if self._OPTIONS.get("multiple_blocking_rate"):
                # получаем время блокировки из settings.BRUTE_GUARD.OPETIONS["base_blocking_rate_minutes"]
                minutes = int(self._OPTIONS.get("base_blocking_rate_minutes"))
                # Увеличиваем время блокировки
                models.Blocked.host_until_increase(REMOTE_ADDR, minutes)
                logger.info(
                    "[%s.until_verify()]: REMOTE_ADDR: %s blocking increased"
                    % (self.__class__.__name__, REMOTE_ADDR)
                )
            raise PermissionDenied

    def until_adding(self, request):
        """
        method for adding remote host to blocking list
        """
        assert isinstance(request, HttpRequest)
        REQUEST_BODY = self.get_request_body(request)
        REMOTE_ADDR = request.META["REMOTE_ADDR"]
        PATH_INFO = request.META["PATH_INFO"]
        KEY = f"{REMOTE_ADDR}:{PATH_INFO}"

        # получаем время получения запросв
        UNTIL = datetime.datetime.fromisoformat(REQUEST_BODY.get("datetime"))
        # определяем время до которого хост будет заблокирован
        UNTIL += datetime.timedelta(
            minutes=self._OPTIONS.get("base_blocking_rate_minutes")
        )
        # создаем запись в моделе Blocked
        row = models.Blocked(
            remote_addr=REMOTE_ADDR,
            path_info=PATH_INFO,
            csrf=REQUEST_BODY.get("csrfmiddlewaretoken"),
            until=UNTIL,
        )
        row.save()
        logger.info(
            "[%s.operation()]: BruteForce detected, REMOTE_ADDR: %s added to blocking list."
            % (self.__class__.__name__, REMOTE_ADDR)
        )
        # Удаляем из очереди записи о попытках для текущего хоста
        self.parent.QUEUE.remove(KEY)
        raise PermissionDenied

    def get_attempts(self, request):
        """
        method for getting attempts list
        """
        assert isinstance(request, HttpRequest)
        REMOTE_ADDR = request.META["REMOTE_ADDR"]
        PATH_INFO = request.META["PATH_INFO"]
        KEY = f"{REMOTE_ADDR}:{PATH_INFO}"

        # получение из очереди списка попыток из для текущего хоста
        result = self.parent.QUEUE.get(KEY)
        result = result if result is not None else []
        logger.debug(
            "[%s.get_attempts()]: result=%s" % (self.__class__.__name__, result)
        )
        return result

    def attempts_counter(self, request):
        assert isinstance(request, HttpRequest)
        REMOTE_ADDR = request.META["REMOTE_ADDR"]
        PATH_INFO = request.META["PATH_INFO"]
        KEY = f"{REMOTE_ADDR}:{PATH_INFO}"
        ATTEMPTS = self.get_attempts(request)
        REQUEST_BODY = self.get_request_body(request)

        # если запрос не пуст
        if len(REQUEST_BODY):
            # добавляем в список попыток новую запись с содержимым запроса
            ATTEMPTS.append(REQUEST_BODY)
            # записываем список попыток в очередь
            self.parent.QUEUE.set(KEY, ATTEMPTS)
        logger.info(
            "[%s.operation()]: ATTEMPTS = %s" % (self.__class__.__name__, len(ATTEMPTS))
        )

    def operation(self, request, response):
        logger.debug("[%s.operation() started]" % self.__class__.__name__)
        assert isinstance(request, HttpRequest)
        assert isinstance(response, HttpResponse)

        self.until_verify(request)
        if hasattr(response, "context_data"):
            self.attempts_counter(request)

        if len(self.get_attempts(request)) >= self._OPTIONS.get(
            "error_attempts_counter"
        ):
            self.until_adding(request)
        logger.debug("[%s.operation() ended]" % self.__class__.__name__)
