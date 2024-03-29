.. File generated by /opt/cloudscheduler/utilities/schema_doc - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the template file ".../cloudscheduler/docs/schema_doc/triggers/trigger_add_htcondor_partition.yaml"
..   2. run the utility ".../cloudscheduler/utilities/schema_doc"
..

Database Trigger: trigger_add_htcondor_partition
================================================

Condition: after insert into condor_machines

.. _trigger_add_htcondor_partition: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_triggers/trigger_add_htcondor_partition.html

.. _trigger_del_htcondor_partition: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_triggers/trigger_del_htcondor_partition.html

This trigger is one of a suite of related triggers maintaining the
status of VMs in relation to their HTCondor job scheduler. The suite
includes:

#. trigger_add_htcondor_partition_

#. trigger_del_htcondor_partition_

Depending on the slot type, this trigger is used to increment by
1 either the *htcondor_partitionable_slots* column or the *htcondor_dynamic_slots* column within the **csv2_vms**
table each time a new row is inserted into the **condor_machines** table.

