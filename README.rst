=============================
Django brute-forece guard
=============================

.. image:: https://badge.fury.io/py/django-brute-guard.svg
    :target: https://badge.fury.io/py/django-brute-guard

.. image:: https://travis-ci.org/dcopm999/django-brute-guard.svg?branch=master
    :target: https://travis-ci.org/dcopm999/django-brute-guard

.. image:: https://codecov.io/gh/dcopm999/django-brute-guard/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/dcopm999/django-brute-guard

Django Brute-force guard

Documentation
-------------

The full documentation is at https://django-brute-guard.readthedocs.io.

Quickstart
----------

Install Django brute-forece guard::

    pip install django-brute-guard

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        "bruteguard",
        ...
    )

    MIDDLEWARE = [
	...
	"bruteguard.middleware.brute_guard",
    ]

    BRUTE_GUARD = {
    "MANAGER": "SingletonManager", # or "DjangoCacheManager"
    "VALIDATORS": ["BruteForceValidator"],
    "OPTIONS": {
            "error_attempts_counter": 5,
            "base_blocking_rate_minutes": 1,
            "multiple_blocking_rate": True,
        },
    }

Add Django brute-forece guard's URL patterns:

.. code-block:: python

    urlpatterns = [
        ...
        path("bruteguard/", include(bruteguard_urls)),
        ...
    ]


Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
