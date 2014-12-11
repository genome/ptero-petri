# PTero Petri API System Tests
To make a new system test, simply create a directory here that contains two
files:

- `net.json`
- `expected_webhooks.yaml`

These files will be used to submit and run a Petri net using a mock web server
to listen to webhooks from the petri worker and respond based on the query
string of the webhook.


## `net.json`
This file contains a [Jinja2](http://jinja.pocoo.org/docs/) template for
specifying a submit request body.  Templating is used only to specify webhook
urls for the Petri service webhooks.  To specify a webhook in net.json, use
the `webhook_url` function inside of a [Jinja2 variable substitution
block](http://jinja.pocoo.org/docs/templates/#variables).  The webhook
function takes the following arguments:

- `webhook_name`: this argument is required and is used to identify the
  webhook in testing
- `request_name`: if present, the mock web server will make an HTTP request to
  the URL associated with the value specified in the webhook request body

All other keyword arguments to the `webhook_url` function will be put into the
requestion body as key value pairs.

Sample usage of the `webhook_url` function:

    {
        "subnets": {
            ...,
            "sample-subnet": {
                "type": "success/failure",
                "url": {{ webhook_url('sample/webhook',
                                       request_name='success',
                                       status_code=123) }}
            },
            ...
        }
    }


## `expected_webhooks.yaml`

This file specifies a DAG for the sequence of webhooks expected and the number
of times each webhook is expected to be called.  The file should contain a top
level dictionary where the keys are the paths of the webhooks received.  The
value for each key should be another dictionary with contains `count`
specifying how many times the webhook should be seen and optionally `depends`,
which is a list of the paths of webhooks that must occur before the webhook
specified in the key.

Sample:

    sample/webhook/single/a:
        count: 1
    sample/webhook/multiple/b:
        count: 3
        depends:
            - sample/webhook/single/a
    sample/webhook/single/c:
        count: 3
        depends:
            - sample/webhook/multiple/b

Consider the situation where a webhook, `B`, depends on another webhook, `A`,
and webhook `A` is expected to be seen 3 times.  In this situation, the
following is considered a valid webhook ordering:

- `A`
- `B`
- `A`
- `A`
