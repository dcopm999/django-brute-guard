=====
Usage
=====

To use Django brute-forece guard in a project, add it to your `INSTALLED_APPS`:

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
