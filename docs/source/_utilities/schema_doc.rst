Utility: schema_doc
===================

Database schema documentation is maintained via the **schema_doc** utility.  
Information about the schema is held in three places:

#. The schema within the database.
#. The schema backup configuration file (*.../cloudscheduler/etc/schema_backup.conf*).
#. The yaml and template .rst files within the documentation directory *.../cloudscheduler/docs/schema_doc*)
   which describe the tables and columns within the database.

The **schema_doc** utility combines these three sources to give complete and accurate information
about the database which changes as features are added or bugs fixed. It also provides functions to
highlight inconsistencies so that accuracy can be maintained.

Synopsis:

To regenerate the restructured text (.rst) files for the database documentation:

* schema_doc

To highlight missing (new) and obsolete database documentation:

* schema_doc list - lists names of tables with new or obsolete information.
* schema_doc show <table_name> - displays the new or obsolete data for the named table.
* schema_doc summary - displays table/column counts.

