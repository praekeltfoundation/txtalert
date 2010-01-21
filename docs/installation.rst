================================================================================
 Installation Instructions for txtAlert
================================================================================

TxtAlert is a hosted internet application. The application can only be accessed over the Internet and it needs to run on a server that has access to the internet.

This document will take you through the steps of installing txtAlert. Some familiarity with the Linux operating system, the python programming language and of databases is assumed.

TxtAlert is an open-source project. All the source code is managed using the `Git`_ version control system. It is hosted at `GitHub <http://github.com/praekelt/txtalert>`_.


Getting the source-code
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

The next steps would be to enable the sending of reminders and pulling in of data from external medical record systems.

.. _`Git`: http://www.git-scm.com 
.. _`Django`: http://www.djangoproject.com
.. _`Admin Interface`: http://127.0.0.1:8000/admin