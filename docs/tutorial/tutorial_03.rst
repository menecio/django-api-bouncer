Part 3 - Adding consumers
=========================
In this section we're going to learn how to add API consumers.
Consumers are associated to individuals using your API, and can be used for
tracking, access management, and more.

*Note:* This section assumes you have enabled the `key-auth` plugin.

1. Create a consumer through the RESTful API
Lets create a user named `John` by issuing the following request:

.. sourcecode:: sh

    $ http -a admin:admin --follow POST http://localhost:8000/consumers/ \
      username=john

Something like this should be your response:

.. sourcecode:: sh

    HTTP/1.0 201 Created
    Allow: GET, POST, HEAD, OPTIONS
    Content-Length: 106
    Content-Type: application/json
    Date: Sun, 10 Sep 2017 10:50:52 GMT
    Server: WSGIServer/0.2 CPython/3.6.1+
    Vary: Accept, Cookie
    X-Frame-Options: SAMEORIGIN

    {
        "created_at": "2017-09-10T10:50:52.562956Z",
        "id": "b437848a-5b76-4371-ba22-6ac6f105870f",
        "username": "john"
    }

You've just added your first consumer.

2. Provision key credentials for your Consumer

Now, we can create a key for our recently created consumer `John` by issuing
the following request:

.. sourcecode:: sh

    $ http -a admin:admin --follow POST http://localhost:8000/consumers/john/key-auth/ \
      key=you_know_nothing

Note: Sending *key* is optional, if you skip it Bouncer will generate a random
key for you.

3. Verify that your Consumer credentials are valid

We can now issue the following request to verify that the credentials of our
John Consumer is valid:

.. sourcecode:: sh

    $ http --follow GET http://localhost:8000/get \
      'Host: httpbin.org' 'apikey: you_know_nothing'


Congratulations! You know the basics now.