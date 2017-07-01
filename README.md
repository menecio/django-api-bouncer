# API Bouncer

[![pypi]][pypi]

API Bouncer is a simple Django app to provide an API
Gateway for micro-services.

Detailed documentation is in the "docs" directory.


# Requirements

* Python (3.5, 3.6)
* Django (1.11)
* Django Rest Framework (3.6)
* PostgreSQL (9.4+)
* psycopg2 (2.5.4+)

# Quick start

1. Add "api_bouncer" to your INSTALLED_APPS setting like this::
```
    INSTALLED_APPS = [
        # all other Django apss you have...
        'api_bouncer',
    ]
```
2. Activate the `key-auth` plugin by adding the middleware on your settings.py::
```python
    MIDDLEWARE = [
        # all other middlewares...
        'api_bouncer.middlewares.key_auth.KeyAuthMiddleware',
    ]
```
3. Include the api_bouncer URLconf in your project urls.py like this::
```python
    url(r'^', include('api_bouncer.urls', namespace='api_bouncer')),
```
4. Run `python manage.py migrate` to create the api_bouncer models.

5. Start the development server and visit http://127.0.0.1:8000/admin/
   to register your APIs (you'll need the Admin app enabled).

[pypi]: https://img.shields.io/badge/pypi-1.0-blue.svg
