===================================
Documentation for txtAlert API v1.0
===================================

The txtAlert API is implemented as REST-ful resource. All relevant data is made available as JSON objects over HTTP. This documentation makes use of `cURL <http://curl.haxx.se/>`_ for all the examples.

Authentication
**************

All clients should authenticate via `HTTP Basic Authentication <http://en.wikipedia.org/wiki/Basic_access_authentication>`_. Since this isn't a very secure authentication mechanism it is advised that all API traffic be done exclusively over HTTPS. At a later stage we'll be looking at supporting `oAuth <http://oauth.net>`_, an authentication based on secure token exchange.

Throttled API calls
*******************

Most API calls are throttled to prevent flooding of the system. Each API subsection in this document will state what the throttling limit is for that call, if any.

=====================
SMS API documentation
=====================

The SMS API allows you to send bulk SMSs and to monitor their delivery status. This delivery status is done asynchronously and requires a second API call.

Sending SMSs
************

Batch send SMSs and receive back an identifier for the batch. The identifier can be used to keep track of the SMS delivery status reports.

Endpoint
    /api/v1/sms.json
    
Throttling
    Allows for 10 calls per minute

Required Parameters
-------------------

:msisdsns: A list of MSISDNs [#fn1]_
:smstext: The text to be sent to the MSISDNs. It should not be longer than 160 characters

An example with cURL::

    $ curl --user 'user:password' \
            --data '{"msisdns": ["271234567890"], "smstext": "hello world!"}' \
            --header 'Content-Type: application/json' \
            http://localhost:8000/api/v1/sms.json
    [
        {
            "status": "v", 
            "status_display": "Unknown", 
            "msisdn": "271234567890", 
            "expiry": "2009-11-24 14:12:44", 
            "delivery": "2009-11-23 14:12:44", 
            "delivery_timestamp": null, 
            "identifier": "04caf966"
        }
    ]
    

SMS delivery status reports
***************************

When sending SMSs you receive a unique identifier for each MSISDN and smstext pair, with it you can track to see what the delivery status is of each SMS.

Endpoint
    /api/v1/sms.json

Throttling
    Allows for 10 calls per minute

Required parameters
-------------------

:since: an `ISO 8601 <http://en.wikipedia.org/wiki/ISO_8601>`_ formatted date time string

An example with cURL::

    $ curl --user 'user:password' \
            --data 'since=2009-11-22 14:12:44+00:00' \
            http://localhost:8000/api/v1/sms.json
    [
        {
            "status": "D", 
            "status_display": "Delivered", 
            "msisdn": "271234567890", 
            "expiry": "2009-11-24 14:12:44", 
            "delivery": "2009-11-23 14:12:44", 
            "delivery_timestamp": "2009-11-23 14:13:10",
            "identifier": "04caf966"
        }
    ]



.. rubric:: Footnotes

.. [#fn1] http://en.wikipedia.org/wiki/MSISDN