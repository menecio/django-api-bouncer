Part 1 - Setup an API gateway in a Minute
=========================================

Scenario
--------
You have multiple private APIs, but you want to consume them from a single
point.

Start your app
--------------
Now that you have successfully installed Django API Bouncer you have access to the
RESTful Admin interface, through which you manage your APIs, consumers, and more.

*Note:* You need a superuser account to access bouncer's admin interface, in this
tutorial, we use assume you have user admin with password admin.

Adding you API
---------------
In this section, you'll be adding your API. This is the first step to having
Django API Bouncer manage your API.

1. Add your API using bouncer's admin interface:

.. sourcecode:: sh

    $ http -a admin:admin --follow POST http://localhost:8000/apis/ \
      name=httpbin-org upstream_url=http://httpbin.org \
      hosts:='["httpbin.org"]'

2. Verify that your API has been added, your response should be similar to this:

.. sourcecode:: sh

    HTTP/1.0 201 Created
    Allow: GET, POST, HEAD, OPTIONS
    Content-Length: 183
    Content-Type: application/json
    Date: Sun, 10 Sep 2017 10:02:35 GMT
    Server: WSGIServer/0.2 CPython/3.6.1+
    Vary: Accept, Cookie
    X-Frame-Options: SAMEORIGIN

    {
        "created_at": "2017-09-10T10:02:35.559631Z",
        "hosts": [
            "httpbin.org"
        ],
        "id": "0df1343a-c7f6-4dcd-b777-25bd5effcbcd",
        "name": "httpbin-org",
        "plugins": [],
        "upstream_url": "https://httpbin.org"
    }

Bouncer is now aware of your API and ready to proxy requests.

3. Forward your requests:

.. sourcecode:: sh

    $ http --follow GET http://localhost:8000/status/418 'Host: httpbin.org'

A successful response means Bouncer is now forwarding requests made to
http://localhost:8000 to the upstream_url we configured in step #1, and is
forwarding the response back to us. And should look like this:

.. sourcecode:: sh

    HTTP/1.0 418 Unknown Status Code
    Content-Length: 135
    Content-Type: text/html
    Date: Sun, 10 Sep 2017 10:10:56 GMT
    Server: WSGIServer/0.2 CPython/3.6.1+
    X-Frame-Options: SAMEORIGIN

        -=[ teapot ]=-

           _...._
         .'  _ _ `.
        | ."` ^ `". _,
        \_;`"---"`|//
          |       ;/
          \_     _/
            `"""`


Bouncer knows to do this through the header defined in the above request:
::
    'Host: <given host>'

Next step is to learn :doc:`how to enable plugins <tutorial_02>`.