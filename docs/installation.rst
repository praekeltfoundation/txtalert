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
    
    ..
    
        ~$ git clone git://github.com/praekelt/txtalert.git

3. The configuration files for txtAlert can be found in the `environments` directory. 

3. Set up your preferred database. This installation will assume you are using SQLite since it is shipped as part of Python version 2.5.

    ..
    
        


.. _`Git`: http://www.git-scm.com 
.. _`Django`: http://www.djangoproject.com