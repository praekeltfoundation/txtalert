txtAlert Operations
===================

Sending of Reminders
~~~~~~~~~~~~~~~~~~~~

A cron job runs every day at noon, this does the following:

#. It imports all data from the MRS.
#. It updates all appointment records based on the MRS import.
#. It sends out reminders according to the latest information.

.. note::   This happens at noon as generally the clinics require up until
            the morning to process the appointment information from the day
            before. Sending it earlier generally results in wrong appointment
            information being sent because the MRS wasn't updated yet by
            the Clinic Admins.

MRS Integration
~~~~~~~~~~~~~~~

Currently txtAlert only integrates with one medical record system,
`Therapy Edge <https://www.ablsa.com/technology/interoperability/sms-interface/>`_.

Therapy Edge provides an XML-RPC interface where on a daily basis appointment
information is available. txtAlert augments its own database of patient and
appointment information with the information that is made available from
this API.

Clinic Admin
~~~~~~~~~~~~

txtAlert provides a Django based Clinic Admin on the ``/clinic/admin/`` path.
This allows clinics without a Medical Record System to still update
patients' appointment information and through that have SMS reminders
sent out.

This interface is multitenant and allows for multiple logins for different
clinics.

CD4 Admin
~~~~~~~~~

Certain Clinics have the ability to also send out CD4 counts to patients
in bulk. This happens in the Django Admin on the ``/admin/cd4/`` path.
The Clinic admin can upload an MS Excel file with the following columns
in the following order:

#. Lab ID number
#. Cellphone number
#. CD4 count

An upload in this format will result in the CD4 counts being applied to the
following message template::

    Hello. Thanks for doing your CD4 test.
    Your CD4 results are back. Your count is [COUNT].
    Please report to %s as soon as possible for further treatment.

txtAlert will update the messages with the delivery status notifications
when they arrive from the mobile networks.

Mobi Bookings
~~~~~~~~~~~~~

There is a simple Mobi based admin designed for small scale use. This is
available on the ``/bookings`` path.

It provides both a patient and a clinic admin interface.

The patient interface allows the patient to view appointments and request
a change.

The clinic admin interface allows a clinic admin to manage patients'
appointments.

.. note::
    The bookings interface is currently not being used nor is it being
    actively maintained.

GDocs Integration
~~~~~~~~~~~~~~~~~

At one point txtAlert allowed for importing of patient records from
Google Docs based spreadsheets. That functionality has been removed as it
was error prone and difficult to maintain. The Clinic Admin has replaced
that functionality.