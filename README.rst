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
        'bruteguard.apps.BruteguardConfig',
        ...
    )

Add Django brute-forece guard's URL patterns:

.. code-block:: python

    from bruteguard import urls as bruteguard_urls


    urlpatterns = [
        ...
        url(r'^', include(bruteguard_urls)),
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
