================================================================================
 Installation Instructions for txtAlert
================================================================================

TxtAlert is a hosted internet application. The application can only be accessed over the Internet and it needs to run on a server that has access to the internet.

This document will take you through the steps of installing txtAlert. Some familiarity with the Linux operating system, the python programming language and of databases is assumed.

TxtAlert is an open-source project. All the source code is managed using the `Git`_ version control system. It is hosted at `GitHub <http://github.com/praekelt/txtalert>`_.


Getting the source-code and starting the application
********************************************************************************

1. Make sure that you have `Git`_ installed and that you can run its commands from a shell. (Enter `git help` at a shell prompt to test this)

2. Clone the git repository with the following command:
    
    ::
    
        ~$ git clone git://github.com/praekelt/txtalert.git
    

3. Set up your preferred database. The configuration files that control all of txtAlert can be found in the `environments` directory. For this installation we'll be using the configuration file `demoy.py` The file configuration `demo.py` is setup for using SQLite which is shipped as part of Python version 2.5.

    ::
    
        ~$ cd ./txtalert
        ~$ ./manage.py syncdb --settings=environments.demo
        Creating table core_msisdn
        Creating table core_language
        Creating table core_clinic
        Creating table core_patient_msisdns
        ...
        You just installed Django's auth system, which means you don't have any superusers defined.
        Would you like to create one now? (yes/no): **yes**
        Username (Leave blank to use 'sdehaan'): **your username**
        E-mail address: **your email address**
        Password: **your password**
        Password (again): **your password**
        Superuser created successfully.
        Installing index for core.Clinic model
        ...
        Installed 13 object(s) from 1 fixture(s)
        ~$

4. Start the server and access the `Admin Interface`_
    
    ::
    
        ~$ ./manage.py runserver --settings=environments.demo
        Validating models...
        0 errors found
        
        Django version 1.2 pre-alpha, using settings 'environments.demo'
        Development server is running at http://127.0.0.1:8000/
        Quit the server with CONTROL-C.
    

You can now log in to the txtAlert `Admin Interface`_ at http://localhost:8000/admin with the username and password you provided at step 3.

The next steps would be to enable the pulling in of data from external medical record systems and the sending of reminders to patients.


Pulling in data from external medical record systems
********************************************************************************

TxtAlert relies on external parties to provide patient and visit data. Currently txtAlert ships with the ability to import code from TherapyEdge. More medical record systems will be added in the near future.


Fetching patient and visit data from TherapyEdge
--------------------------------------------------------------------------------

TherapyEdge has an XML-RPC service that publishes patient and visit data. In order to import the data you need to provide txtAlert with a username and password for the XML-RPC service.

Go to the `Admin Interface`_ and add two new settings:

1. `THERAPYEDGE_USERNAME` of type text and the value is the username that TherapyEdge has provided you with.
2. `THERAPYEDGE_PASSWORD`, also of type text and the value is the password that TherapyEdge has provided you with.

Then from the command line execute the following:

    ..
    
        ~$ ./manage.py te_import_data --settings=environments.demo
    
This will import all TherapyEdge patient and visit data of the previous day, midnight to midnight.

This command can be configured with `cron` to run at specific times each day.

Sending of reminders
********************************************************************************

With the data received from the external medical record system txtAlert can now send out timed reminders over SMS. 

In order to send messages an SMS backend needs to be configured. TxtAlert currently ships with a backend that supports the sending of SMSs via `Opera`_. In order to use the `Opera`_ backend please specify the following settings in `environments/demo.py`. These values should be provided to you by `Opera`_.

    ::
    
        SMS_GATEWAY_CLASS = 'gateway.backends.opera'
        OPERA_SERVICE = '**your opera service id**'
        OPERA_PASSWORD = '**your opera password**'
        OPERA_CHANNEL = '**your opera channel id**'
        
    
TxtAlert is configured to send reports over email and SMS for each time it sends out reminders. Go to the `Admin Interface`_ and the following two settings:

1. `Stats MSISDNs` of type text and with the phone number you want the report SMSed to as the value
2. `Stats Emails` of type text and with the email address you want the report to be emailed to.

The values can have multiple numbers or email addresses as long as they are each one a single line.

The sending of reminders is currently configured to send messages at the following intervals:

1. Two weeks in advance reminding the patient of the clinic appointment
2. Day in advance reminding the patient of the clinic appointmnet
3. The day after either thanking a patient for attendance or alerting the patient of the missed appointment and urging him/her to reschedule.

Execute the following command from the command line in order to send out the reminders:

    ..
    
        ~$ ./manage.py te_send_reminders --settings=environments.demo
    
This command can be configured with `cron` to run at specific times each day.


.. _`Git`: http://www.git-scm.com 
.. _`Django`: http://www.djangoproject.com
.. _`Admin Interface`: http://127.0.0.1:8000/admin
.. _`Opera`: http://dragon.sa.operatelecom.com/