trigger_add_htcondor_partition
==============================

Depending on the slot type, this trigger is used to increment by 1 either the
*htcondor_partitionable_slots* column or the *htcondor_dynamic_slots* column
within the **csv2_vms** table each time a new row is inserted into the 
**cloud_machines** table.
