Documentation for txtAlert API
==============================

Please Call Me API documentation
--------------------------------

A "Please Call Me" is a text message that is sent from one subscriber to
another where asking the latter to call the sender of the message back.

PCMs (Please Call Me's) are usually sent by dialing a specific USSD code
and arrive at the receivers handset as a sponsored SMS message informing
the receiver of the request.

In South Africa all major telecom operators provide a number of free
PCMs, to all subscribers. This allows for those who cannot afford
credit on their phones to still communicate when needed.

In txtAlert PCMs are used as a low-cost means for the patient and the
clinic to get in touch. When a patient is unable to attend an
appointment, he or she can send a PCM to txtAlert. This PCM is
registered by txtAlert and the the patient is identified by the MSISDN.
The clinic is notified of the PCM and will call the patient back to
schedule a new appointment.

Registering PCMs
----------------

URI
    /api/v1/pcm.json
HTTP Method
    POST

Parameters
~~~~~~~~~~

:sender_msisdn: The MSISDN sending the PCM
:sms_id: Unique ID from the SMSC
:recipient_msisdn: The MSISDN receiving the PCM
:message_content: The original PCM message (optional)

or

Using HTTP to post the JSON of `Vumi <https://github.com/praekelt/vumi/>`_
message to the URL.

Example
~~~~~~~

An example of HTTP POSTing with parameters with cURL::

    $ curl --user 'user:password' \
    >        --data 'sender_msisdn=271234567890&sms_id=abfegvcd&recipient_msisdn=271234567810' \
    >        http://localhost:8000/api/v1/pcm.json
    Please Call Me registered

`FrontlineSMS <http://www.frontlinesms.com>`_ supports this out of the box.
Check the `FrontlineSMS <http://www.frontlinesms.com>`_ documentation for
how to do this.

An example of HTTP POSTing JSON from Vumi's APIs with cURL::

    $ curl --user 'user:password' \
    >   --data '{"from_addr": "271234567890", "to_addr": "271234567890", "content":"message", "message_id": "abfegvcd"}' \
    >   http://localhost:8000/api/v1/pcm.json


Both API calls:

1. return an ``HTTP 201 Created`` header if successful.
2. return an ``HTTP 409 Conflict`` if an exact same SMS was received
   in the last 2 hours.
3. return an ``HTTP 400 Bad Request`` if not all parameters are present.

Sending SMSs
------------

SMSs are sent via Vumi Go's HTTP API. txtAlert should have an account
configured and appropriate token set to allow for outbound messaging.

Receiving Delivery Reports
--------------------------

The path for receiving network acknowledgements & delivery reports is::

    /api/v1/events.json

This URL endpoint expects a Vumi event message. Event messages of type ``ack``
and ``delivery_report`` are supported. These update the original outbound
message with the appropriate txtAlert status matching pending, failed
or delivered.
