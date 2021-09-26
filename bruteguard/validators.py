import datetime
import logging
from typing import Dict

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from bruteguard import models
from bruteguard.patterns.composite import Leaf

logger = logging.getLogger(__name__)


class BruteForceValidator(Leaf):
    OPTIONS = settings.BRUTE_GUARD.get("OPTIONS")

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

        REMOTE_ADDR = request.META["REMOTE_ADDR"]
        REQUEST_BODY = self.get_request_body(request)
        PATH_INFO = request.META["PATH_INFO"]
        KEY = f"{REMOTE_ADDR}:{PATH_INFO}"
        ATTEMPTS = self.parent.QUEUE.get(KEY)
        ATTEMPTS = ATTEMPTS if ATTEMPTS is not None else []

        logger.debug(
            "[%s.operation()]: request not authenticated" % self.__class__.__name__
        )

        logger.debug(
            "[%s.operation()]: GUARDS OPTIONS = %s"
            % (self.__class__.__name__, self.OPTIONS)
        )
        logger.debug(
            "[%s.operation()]: PATH_INFO = %s" % (self.__class__.__name__, PATH_INFO)
        )
        logger.debug(
            "[%s.operation()]: REMOTE_ADDR = %s"
            % (self.__class__.__name__, REMOTE_ADDR)
        )
        logger.debug(
            "[%s.operation()]: ATTEMPTS = %s" % (self.__class__.__name__, len(ATTEMPTS))
        )
        logger.debug(
            "[%s.operation()]: REQUEST_BODY = %s"
            % (self.__class__.__name__, REQUEST_BODY)
        )
        logger.debug("[%s.operation()]: KEY = %s" % (self.__class__.__name__, KEY))

        # Находим записи в моделе для REMOTE_ADDR у которых  until больше текущего времени
        queryset = models.Blocked.objects.filter(
            remote_addr=REMOTE_ADDR, until__gt=datetime.datetime.now()
        )

        # Если такая запись есть
        if queryset.exists():
            logger.debug(
                "[%s.operation()]: REMOTE_ADDR: %s blocked."
                % (self.__class__.__name__, REMOTE_ADDR)
            )
            # Если в настройках проекта settings.BRUTE_GUARD.OPTIONS['multiple_blocking_rate'] = True
            if self.OPTIONS.get("multiple_blocking_rate", False):
                # При каждом новом запросе от заблокированного REMOTE_ADDR увеличиваем until время блокировки еще на
                # settings.BRUTE_GUARD.OPTIONS.get("base_blocking_rate_minutes") минут
                row = queryset.last()
                row.until += datetime.timedelta(
                    minutes=self.OPTIONS.get("base_blocking_rate_minutes")
                )
                row.save()
                logger.debug(
                    "[%s.operation()]: REMOTE_ADDR: %s blocking has been increased to %s."
                    % (self.__class__.__name__, REMOTE_ADDR, row.until)
                )
            # Вызываем исключение PermissionDenied
            raise PermissionDenied

        if hasattr(response, "context_data") and not response.context_data.get(
            "has_permission"
        ):
            if len(REQUEST_BODY):
                if self.parent.QUEUE.has_key(KEY):  # noqa
                    ATTEMPTS.append(REQUEST_BODY)
                else:
                    ATTEMPTS = [REQUEST_BODY]
                self.parent.QUEUE.set(KEY, ATTEMPTS)

        if len(ATTEMPTS) >= self.OPTIONS.get("error_attempts_counter"):
            print(REQUEST_BODY.get("datetime"))
            UNTIL = datetime.datetime.fromisoformat(REQUEST_BODY.get("datetime"))
            UNTIL += datetime.timedelta(
                minutes=self.OPTIONS.get("base_blocking_rate_minutes")
            )
            row = models.Blocked(
                remote_addr=REMOTE_ADDR,
                path_info=PATH_INFO,
                username=REQUEST_BODY.get("username"),
                password=REQUEST_BODY.get("password"),
                csrf=REQUEST_BODY.get("csrfmiddlewaretoken"),
                until=UNTIL,
            )
            row.save()
            self.parent.QUEUE.remove(KEY)
            logger.debug(
                "[%s.operation()]: BruteForce detected, REMOTE_ADDR: %s blocked."
                % (self.__class__.__name__, REMOTE_ADDR)
            )
            raise PermissionDenied

        logger.debug("[%s.operation() ended]" % self.__class__.__name__)
