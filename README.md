# API Bouncer

[![build-status-image]][travis]
[![coverage-image]][coverage]
[![pypi-version]][pypi]

API Bouncer is a simple Django app to provide an API
Gateway for micro-services.

It's heavily inspired by [Kong][kong]


# Requirements

* Python (3.5, 3.6)
* Django (1.10, 1.11)
* Django Rest Framework (3.6)
* PostgreSQL (9.4+)
* psycopg2 (2.5.4+)

# Quick start

Add "api_bouncer" to your INSTALLED_APPS setting like this:

```python
    INSTALLED_APPS = [
        # all other Django apss you have...
        'api_bouncer',
    ]
```

Activate the `key-auth` plugin by adding the middleware on your settings.py:

```python
    MIDDLEWARE = [
        # all other middleware...
        'api_bouncer.middleware.bouncer.BouncerMiddleware',  # required
        'api_bouncer.middleware.key_auth.KeyAuthMiddleware',
    ]
```

Important! 
Note that you need to include `BouncerMiddleware` before the rest of plugin
middleware. Otherwise it will **not** work. 


Include the api_bouncer URLconf in your project urls.py like this:

```python
    url(r'^', include('api_bouncer.urls', namespace='api_bouncer')),
```

Run `python manage.py migrate` to create the api_bouncer models.

# Available plugins

#### Authenticacion
- **Key authentication:** Add key authentication to your API

#### Security
- **ACL:** Control which consumers have access to your API
- **IP restriction:** Blacklist or whilelist IPs that can access your API 

#### Traffic Control
- **Request termination:** Terminate all request with a specific response.

# Documentation
Documentation can be found in the `docs` directory or [here][docs]


[coverage-image]: https://coveralls.io/repos/github/menecio/django-api-bouncer/badge.svg?branch=master
[coverage]: https://coveralls.io/github/menecio/django-api-bouncer?branch=master
[build-status-image]: https://travis-ci.org/menecio/django-api-bouncer.svg?branch=master
[travis]: https://travis-ci.org/menecio/django-api-bouncer?branch=master
[pypi-version]: https://img.shields.io/badge/pypi-0.3-blue.svg
[pypi]: https://pypi.python.org/pypi/django-api-bouncer
[kong]: https://getkong.org
[docs]: http://www.menecio.me/django-api-bouncer/docs
