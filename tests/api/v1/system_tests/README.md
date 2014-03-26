# PTero Petri API System Tests
To make a new system test, simply create a directory here that contains two
files:

- `net.json`
- `expected_callbacks.yaml`

These files will be used to submit and run a Petri net using a mock web server
to listen to callbacks from the petri worker and respond based on the query
string of the callback.


## `net.json`
This file contains a [Jinja2](http://jinja.pocoo.org/docs/) template for
specifying a submit request body.  Templating is used only to specify callback
urls for the Petri service webhooks.  To specify a callback in net.json, use
the `callback_url` function inside of a [Jinja2 variable substitution
block](http://jinja.pocoo.org/docs/templates/#variables).  The callback
function takes the following arguments:

- `callback_name`: this argument is required and is used to identify the
  callback in testing
- `request_name`: if present, the mock web server will make an HTTP request to
  the URL associated with the value specified in the webhook request body

All other keyword arguments to the `callback_url` function will be put into the
requestion body as key value pairs.

Sample usage of the `callback_url` function:

    {
        "subnets": {
            ...,
            "sample-subnet": {
                "type": "success/failure",
                "url": {{ callback_url('sample/callback',
                                       request_name='success',
                                       status_code=123) }}
            },
            ...
        }
    }


## `expected_callbacks.yaml`

This file specifies a DAG for the sequence of callbacks expected and the number
of times each callback is expected to be called.  The file should contain a top
level dictionary where the keys are the paths of the callbacks received.  The
value for each key should be another dictionary with contains `count`
specifying how many times the callback should be seen and optionally `depends`,
which is a list of the paths of callbacks that must occur before the callback
specified in the key.

Sample:

    sample/callback/single/a:
        count: 1
    sample/callback/multiple/b:
        count: 3
        depends:
            - sample/callback/single/a
    sample/callback/single/c:
        count: 3
        depends:
            - sample/callback/multiple/b

Consider the situation where a callback, `B`, depends on another callback, `A`,
and callback `A` is expected to be seen 3 times.  In this situation, the
following is considered a valid callback ordering:

- `A`
- `B`
- `A`
- `A`
