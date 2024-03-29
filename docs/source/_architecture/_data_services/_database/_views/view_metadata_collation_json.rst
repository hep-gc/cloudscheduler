.. File generated by /opt/cloudscheduler/utilities/schema_doc - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the template file ".../cloudscheduler/docs/schema_doc/views/view_metadata_collation_json.yaml"
..   2. run the utility ".../cloudscheduler/utilities/schema_doc"
..

Database View: view_metadata_collation_json
===========================================

.. _view_active_resource_shortfall: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_active_resource_shortfall.html

.. _view_available_resources: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_available_resources.html

.. _view_groups_of_idle_jobs: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_groups_of_idle_jobs.html

.. _view_idle_vms: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_idle_vms.html

.. _view_metadata_collation_json: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_metadata_collation_json.html

.. _view_resource_contention: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_resource_contention.html

This view is one of a suite of related views used by
the VM scheduler to control the management of VMs. The suite includes:

#. view_active_resource_shortfall_

#. view_available_resources_

#. view_groups_of_idle_jobs_

#. view_idle_vms_

#. view_metadata_collation_json_

#. view_resource_contention_

The **view_metadata_collation_json** is used by the VM scheduler to build the stream
of VM contextualization metadata files in the correct order for the cloud's
metadata service. This view converts into a json string the output of
the User Interface (UI) view_metadata_collation_ which creates a customized list of metadata
files in priority order for each group/cloud. Only enabled metadata files are
included and each group/cloud can specifically exclude from their customized list specific
metadata files by name.

.. _view_metadata_collation: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_metadata_collation.html


Columns:
^^^^^^^^

* **group_metadata** (String):

      Is a json string containing the entire output from the User Interface
      (UI) view_metadata_collation_.

      .. _view_metadata_collation: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_metadata_collation.html

