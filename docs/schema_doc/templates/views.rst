Views
=====

.. _Accounting: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_apel_accounting.html

.. _Status: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_cloud_status.html

.. _Metadata: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_metadata_collation.html

.. _User: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_user_groups.html

.. _Scheduling: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_groups_of_idle_jobs.html

.. _Quota: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_vm_kill_retire_over_quota.html

A database view is created by a user defined SQL statement pulling and manipulating
data from one or more tables to present a derived or read-only table.
CSV2 makes extensive use of views for both presentation and decision making.

To aid in the understanding and purpose of each view, they are grouped in the
following functional categories:

* Accounting_
* User Interface:

    * `Cloud Status`__
    * `Metadata Management`__
    * `User Management`__

__ Status_

__ Metadata_

__ User_

* Virtual Machine Management:

    * `VM Scheduling`__
    * `Quota Compliance`__

__ Scheduling_

__ Quota_

.. toctree::
   :maxdepth: 1
   :caption: Alternatively, here is the list of all the views:

