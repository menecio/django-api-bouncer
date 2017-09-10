Installation
============

Install with pip
::
    pip install django-api-bouncer

Add `api_bouncer` to your `INSTALLED_APPS`

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'api_bouncer',
    )

Add `BouncerMiddleware` to your settings.py

.. code-block:: python

    MIDDLEWARE = [
        ...
        'api_bouncer.middleware.bouncer.BouncerMiddleware',
    ]

Add the following to your urls.py

.. code-block:: python

    urlpatterns = [
        ...
        url(r'^', include('api_bouncer.urls', namespace='api_bouncer')),
    ]

Sync your database
------------------

.. sourcecode:: sh

    $ python manage.py migrate api_bouncer

Next step is our :doc:`first tutorial <tutorial/tutorial_01>`.