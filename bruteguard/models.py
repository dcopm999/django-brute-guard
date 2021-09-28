# -*- coding: utf-8 -*-
import datetime
import logging

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Blocked(models.Model):
    remote_addr = models.GenericIPAddressField(verbose_name=_("REMOTE_ADDR"))
    path_info = models.TextField(verbose_name=_("PATH_INFO"))
    csrf = models.CharField(max_length=100, verbose_name=_("CSRF"))
    until = models.DateTimeField(editable=False, verbose_name=_("UNTIL"))
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name=_("Created")
    )
    updated = models.DateTimeField(
        auto_now=True, editable=False, verbose_name=_("Updated")
    )

    def __str__(self):
        return f"{self.remote_addr}"

    @classmethod
    def host_until_gt_now(self, remote_addr: str):
        assert isinstance(remote_addr, str)
        return self.objects.filter(remote_addr=remote_addr, until__gt=timezone.now())

    @classmethod
    def host_is_blocked(self, remote_addr: str):
        assert isinstance(remote_addr, str)
        result = self.host_until_gt_now(remote_addr).exists()
        logger.debug(
            "[%s.host_is_blocked(%s)]: result=%s."
            % (self.__class__.__name__, remote_addr, result)
        )
        return result

    @classmethod
    def host_until_increase(self, remote_addr: str, minutes: int):
        assert isinstance(remote_addr, str)
        assert isinstance(minutes, int)
        row = self.host_until_gt_now(remote_addr).last()
        row.until += datetime.timedelta(minutes=minutes)
        row.save()
        logger.debug(
            "[%s.host_until_increase(%s)]: blocking has been increased to %s"
            % (self.__class__.__name__, remote_addr, row.until)
        )

    class Meta:
        verbose_name = _("Blocked")
        verbose_name_plural = _("Blocked")
        get_latest_by = "until"
