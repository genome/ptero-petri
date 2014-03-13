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
specifying a submit request body.

Available template variables:

- `callback_port`:  port on localhost where the mock callback web server listens


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


## Callback URL Construction
Callback URLs contain two kinds of information:

- an identifier so that the callback can be recognized for testing
- instructions for the mock service to make a follow-up HTTP request

The identifier is simply the path of the URL without the leading slash.  The
instructions for the follow-up request are controlled by the query string of
the URL.
