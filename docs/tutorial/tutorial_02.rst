Part 2 - Enabling plugins
=========================
Plugins allow you to easily add new features to your API or make your API
easier to manage.

In the steps below you will configure the `key-auth` plugin to add authentication
to your API. Prior to the addition of this plugin, all requests to your API
would be proxied upstream.

Once you add and configure this plugin, only requests with the correct API
key(s) will be proxied - all other requests will be rejected, thus protecting
your upstream service from unauthorized use.

1. Configure the key-auth plugin for your API

.. sourcecode:: sh

    $ http -a admin:admin --follow POST localhost:8000/apis/httpbin-org/plugins/ \
      name=key-auth

*Note:* This plugin also accepts a config.key_names parameter, which defaults to
[apikey]. It is a list of headers and parameters names (both are supported)
that are supposed to contain the API key during a request.

2. Verify that the plugin is properly configured

.. sourcecode:: sh

    $ http --follow GET http://localhost:8000/get 'Host: httpbin.org'

Since you did not specify the required *apikey* header or parameter,
the response should be::

    401 Unauthorized


Next step is to learn :doc:`how to add consumers <tutorial_03>`.