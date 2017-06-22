# API Bouncer

API Bouncer is a simple Django app to provide an API
Gateway for micro-services.

Detailed documentation is in the "docs" directory.


# Requirements

* Python (3.5, 3.6)
* Django (1.11)
* Django Rest Framework (3.6)
* PostgreSQL (9.3+)
* psycopg2 (2.5.4+)

# Quick start

1. Add "api_bouncer" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'api_bouncer',
    ]

2. Include the api_bouncer URLconf in your project urls.py like this::

    url(r'^api-bouncer/', include('api_bouncer.urls')),

3. Run `python manage.py migrate` to create the api_bouncer models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to register your APIs (you'll need the Admin app enabled).

