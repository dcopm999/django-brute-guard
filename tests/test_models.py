#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-brute-guard
------------

Tests for `django-brute-guard` models module.
"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from bruteguard import models


class BlockedModelCase(TestCase):
    def setUp(self):
        self.row = {
            "remote_addr": "127.0.0.1",
            "path_info": "/",
            "csrf": "qwerty",
            "until": timezone.now() + timedelta(minutes=5),
        }
        self.query = models.Blocked.objects.create(**self.row)

    def test_str(self):
        self.assertEqual(self.query.__str__(), self.row["remote_addr"])

    def test_host_unitl_gt_now(self):
        result = models.Blocked.host_until_gt_now("127.0.0.1")
        self.assertIn(self.query, result)

    def test_host_is_blocked(self):
        self.assertTrue(models.Blocked.host_is_blocked("127.0.0.1"))

    def test_host_until_increase(self):
        models.Blocked.host_until_increase("127.0.0.1", 10)
        self.assertEqual(
            models.Blocked.objects.get(remote_addr="127.0.0.1").until,
            self.row["until"] + timedelta(minutes=10),
        )

    def tearDown(self):
        pass
