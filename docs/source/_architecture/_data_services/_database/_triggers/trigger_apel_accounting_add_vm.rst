.. File generated by /opt/cloudscheduler/utilities/schema_doc - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the template file ".../cloudscheduler/docs/schema_doc/triggers/trigger_apel_accounting_add_vm.yaml"
..   2. run the utility ".../cloudscheduler/utilities/schema_doc"
..

Database Trigger: trigger_apel_accounting_add_vm
================================================

Condition: after insert into csv2_vms

.. _trigger_apel_accounting_add: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_triggers/trigger_apel_accounting_add_vm.html

.. _trigger_apel_accounting_del: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_triggers/trigger_apel_accounting_del_vm.html

This trigger is one of a suite of related triggers accumulating accounting
information. The suite includes:

#. trigger_apel_accounting_add_

#. trigger_apel_accounting_del_

This trigger creates an accounting record for each new VM. Subsequently these
accounting recoreds are updated periodically by the VM data poller throughout the
life of the VM.

