.. File generated by /opt/cloudscheduler/utilities/schema_doc - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the template file ".../cloudscheduler/docs/schema_doc/triggers/trigger_csv2_configuration_update.yaml"
..   2. run the utility ".../cloudscheduler/utilities/schema_doc"
..

Database Trigger: trigger_csv2_configuration_update
===================================================

Condition: after update on csv2_configuration

This view maintains a timestamp in the **csv2_timestamps** table of the last
update to the CSV2 configuration. For processes using the **db_config.refresh()** library function,
the timestamp is used to determine whether the caller's configuration is already
up to date or whether it needs to be refreshed from the
database.

