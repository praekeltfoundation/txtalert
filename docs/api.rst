================================================================================
 Documentation for txtAlert API v1.0
================================================================================

The txtAlert API is implemented as REST-ful resource. All relevant data is made available as JSON objects over HTTP. This documentation makes use of `cURL <http://curl.haxx.se/>`_ for all the examples.

Authentication
********************************************************************************

All clients should authenticate via `HTTP Basic Authentication <http://en.wikipedia.org/wiki/Basic_access_authentication>`_. Since this isn't a very secure authentication mechanism it is advised that all API traffic be done exclusively over HTTPS. At a later stage we'll be looking at supporting `oAuth <http://oauth.net>`_, an authentication based on secure token exchange.

Throttled API calls
********************************************************************************

Most API calls are throttled to prevent flooding of the system. Each API subsection in this document will state what the throttling limit is for that call, if any.

================================================================================
 SMS API documentation
================================================================================

The SMS API allows you to send bulk SMSs and to monitor their delivery status. This delivery status is done asynchronously and requires a second API call.

Sending SMSs
********************************************************************************

Batch send SMSs and receive back an identifier for the batch. The identifier can be used to keep track of the SMS delivery status reports.

URI
    /api/v1/sms.json
HTTP Method
    POST

Throttling
    Allows for 10 calls per minute

Parameters
--------------------------------------------------------------------------------

:msisdsns: A list of unique `MSISDNs <http://en.wikipedia.org/wiki/MSISDN>`_
:smstext: The text to be sent to the MSISDNs. It should not be longer than 160 characters. **Note:** The must be posted as a JSON object, not HTTP post key value pair variables.

Example
--------------------------------------------------------------------------------

An example with cURL::

    $ curl --user 'user:password' \
    >        --data '{"msisdns": ["271234567890"], "smstext": "hello world!"}' \
    >        --header 'Content-Type: application/json' \
    >        http://localhost:8000/api/v1/sms.json
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

If more than one SMS was sent in this batch the JSON list will return multiple JSON objects. All will have the same `identifier` but different `msisdn` values.

SMS delivery status reports
********************************************************************************

When sending SMSs you receive a unique identifier for each MSISDN and smstext pair, with it you can track to see what the delivery status is of each SMS.

URI
    /api/v1/sms.json
HTTP Method
    GET

Throttling
    Allows for 10 calls per minute.

Required parameters
--------------------------------------------------------------------------------

:since: an `ISO 8601 <http://en.wikipedia.org/wiki/ISO_8601>`_ formatted date time string

Example
--------------------------------------------------------------------------------

An example with cURL::

    $ curl --user 'user:password' \
    >        --get \
    >        --data 'since=2009-11-22%2014:12:44+00:00' \
    >        http://localhost:8000/api/v1/sms.json
    [
        {
            "status": "D", 
            "status_display": "Delivered", 
            "msisdn": "271234567890", 
            "expiry": "2009-11-24 14:12:44", 
            "delivery": "2009-11-23 14:12:44", 
            "delivery_timestamp": "2009-11-23 14:13:10",
            "identifier": "04caf966"
        },
        {
            ...
        },
        {
            ...
        }
    ]

This will return JSON status objects for all SMSs sent since the date specified in the `since` parameter.

Retrieving a single delivery status report
********************************************************************************

URI
    /api/v1/sms/<identifier>/<msisdn>.json
HTTP Method
    GET

Throttling
    Allows for 10 calls per minute.

Required parameters
--------------------------------------------------------------------------------

None, other than the `identifier` and the `msisdn` in the URI.

Example
--------------------------------------------------------------------------------

An example with cURL::

    $ curl --user 'user:password' \
    >        --get \
    >        --data 'since=2009-11-22%2014:12:44+00:00' \
    >        http://localhost:8000/api/v1/sms/04caf966/271234567890.json
    {
        "status": "D", 
        "status_display": "Delivered", 
        "msisdn": "271234567890", 
        "expiry": "2009-11-24 14:12:44", 
        "delivery": "2009-11-23 14:12:44", 
        "delivery_timestamp": "2009-11-23 14:13:10",
        "identifier": "04caf966"
    }

This will return JSON status objects for all SMSs sent since the date specified in the `since` parameter.

================================================================================
 Please Call Me API documentation
================================================================================

A "Please Call Me" is a text message that is sent from one subscriber to another where asking the latter to call the sender of the message back. PCMs (Please Call Me's) are usually sent by dialing a specific USSD line and arrive at the receivers handset as a sponsored SMS message informing the receiver of the request. In South Africa all major telecom operators provide a number of free PCMs, to all subscribers. This allows for those who cannot afford credit on their phones to still communicate when needed.

In txtAlert PCMs are used as a low-cost means for the patient and the clinic to get in touch. When a patient is unable to attend an appointment, he or she can send a PCM to txtAlert. This PCM is registered by txtAlert and the the patient is identified by the MSISDN. The clinic is notified of the PCM and will call the patient back to schedule a new appointment.

Registering PCMs
********************************************************************************

TxtAlert hasn't settled on a single method of registering PCMs yet. The current infrastructure supports HTTP POSTing of the necessary variables to a specific URI. **Note**: This is different from sending SMSs where a JSON object needs to be posted as raw post data.

URI
    /api/v1/pcm.json
HTTP Method
    POST

Parameters
--------------------------------------------------------------------------------

:sender_msisdn: The MSISDN sending the PCM
:sms_id: Unique ID from the SMSC
:recipient_msisdn: The MSISDN receiving the PCM
:message_content: The original PCM message (optional)

Example
--------------------------------------------------------------------------------

An example with cURL::

    $ curl --user 'user:password' \
    >        --data 'sender_msisdn=271234567890&sms_id=abfegvcd&recipient_msisdn=271234567810' \
    >        http://localhost:8000/api/v1/pcm.json
    Please Call Me registered

The API returns with an `HTTP 201 Created` header.

`FrontlineSMS <http://www.frontlinesms.com>`_ supports this out of the box. Check the `FrontlineSMS <http://www.frontlinesms.com>`_ documentation for how to do this.

Retrieving PCMs
********************************************************************************

TxtAlert provides a means of retrieving all PCMs received since a specific point in time.

URI
    /api/v1/pcm.json
HTTP Method
    GET

Parameters
--------------------------------------------------------------------------------

:since: an `ISO 8601 <http://en.wikipedia.org/wiki/ISO_8601>`_ formatted date time string

Example
--------------------------------------------------------------------------------

An example with cURL::
    
    $ curl --user 'user:password' \
    >        --get \
    >        --data 'since=2009-11-22%2014:12:44+00:00' \
    >        http://localhost:8000/api/v1/pcm.json
    [
        {
            "created_at": "2009-11-25 11:23:50", 
            "sender_msisdn": "271234567890", 
            "recipient_msisdn": "271234567810", 
            "sms_id": "abfegvcd"
        }, 
        {
            ...
        }, 
        {
            ...
        }
    ]
