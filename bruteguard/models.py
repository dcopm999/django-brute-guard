# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _


class Blocked(models.Model):
    remote_addr = models.GenericIPAddressField(verbose_name=_("REMOTE_ADDR"))
    path_info = models.TextField(verbose_name=_("PATH_INFO"))
    username = models.CharField(max_length=100, verbose_name=_("USERNAME"))
    password = models.CharField(max_length=100, verbose_name=_("PASSWORD"))
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

    class Meta:
        verbose_name = _("Blocked")
        verbose_name_plural = _("Blocked")
        get_latest_by = "until"
