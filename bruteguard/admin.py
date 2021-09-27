# -*- coding: utf-8 -*-
from django.contrib import admin

from bruteguard import models


@admin.register(models.Blocked)
class BlockedAdmin(admin.ModelAdmin):
    list_display = [
        "remote_addr",
        "path_info",
        "until",
        "created",
        "updated",
    ]
    list_filter = ["remote_addr"]
    search_fields = ["remote_addr"]
    date_hierarchy = "created"
