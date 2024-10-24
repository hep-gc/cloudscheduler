.. File generated by /opt/cloudscheduler/utilities/schema_doc - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the template file ".../cloudscheduler/docs/schema_doc/views/view_cloud_status_slot_summary.yaml"
..   2. run the utility ".../cloudscheduler/utilities/schema_doc"
..

Database View: view_cloud_status_slot_summary
=============================================

.. _view_cloud_status: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_cloud_status.html

.. _view_cloud_status_flavor_slot_detail_summary: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_cloud_status_flavor_slot_detail_summary.html

.. _view_cloud_status_flavor_slot_detail: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_cloud_status_flavor_slot_detail.html

.. _view_cloud_status_flavor_slot_summary: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_cloud_status_flavor_slot_summary.html

.. _view_cloud_status_slot_detail_summary: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_cloud_status_slot_detail_summary.html

.. _view_cloud_status_slot_detail: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_cloud_status_slot_detail.html

.. _view_cloud_status_slot_summary: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_cloud_status_slot_summary.html

.. _view_job_status: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_job_status.html

.. _view_vms: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_vms.html

.. _timeseries: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_condor_jobs_group_defaults_applied.html

This view is one of a suite of related views supporting the
primary status display of CSV2. The suite includes:

#. view_cloud_status_ (also used by timeseries_)

#. view_cloud_status_flavor_slot_detail_summary_

#. view_cloud_status_flavor_slot_detail_

#. view_cloud_status_flavor_slot_summary_

#. view_cloud_status_slot_detail_summary_

#. view_cloud_status_slot_detail_ (also used by timeseries_)

#. view_cloud_status_slot_summary_

#. view_job_status_ (also used by timeseries_)

#. view_vms_

While view #1 provides slot totals, views #2 through #7 present additional
slot information. In the CLI, this additional slot information is available as
optional tables (see the '--with' option in the CLI documentation). In the
web interface, the additional slot information is presented in the group/cloud expanded
view in one of four user selectable styles controlled by the following
user settings:'

a) Enable slot detail.

b) Enable slot flavor information.

With niether user setting enabled, the expanded view of the web cloud
status will present **view_cloud_status_slot_summary** information.


Columns:
^^^^^^^^

* **group_name** (String(32)):

      Is the name of the group owning the cloud.

* **cloud_name** (String(32)):

      Is the name of the cloud hosting the HTCondor dynamic slots.

* **busy** (Integer):

      Is the number HTCondor dynamic slots that are currently running jobs.

* **idle** (Integer):

      Is the number HTCondor dynamic slots that are currently idle.

* **idle_percent** (Integer):

      Is calculate as **idle** times 100 divided by the aggregate of **idle**
      plus **busy**.

