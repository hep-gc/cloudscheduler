Utility: schema_backup
======================

schema_backup reads the CSV2 database and creates backups of both table structures and
non-ephemeral table data to the standard and user data backup directories (see **configuration**
below). It is normally invoked during the upgrade process by the **db_upgrade** utility
but should also be run regularly as a stand-alone utility to backup user data.

Synopsis: schema_backup

What gets backed up and where?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tables are divided into four categories (see **configuration** below  and 
:doc:`../_architecture/_data_services/_database/_tables/index`)
for security, and upgrade purposes and are backed up as follows:

* All table structures and all global configuration data is saved in a host specific 
  subdirectory of the *CSV2 backup directory* (configurable).
  By default, the CSV2
  backup directory is *.../cloudscheduler/schema/schema_backup*.
* All user data (and table structures) is saved in the *user data backup directory* (configurable).
* Ephemeral data is ignored and not saved.

Configuration
^^^^^^^^^^^^^

schema_backup, and other utilities, are configured by the YAML file 
* **.../cloudscheduler/etc/schema_backup.conf**. This file identifies the backup directories, database
service provider and consumers, and the categorization of the tables within the CSV2 database. The
following parameters are recognozed from this file:

* **csv2_backup_dir** - specifies the full path of a local filesystem directory to be used as the
  CSV2 backup directory. It is recommended that this directory is also within a git/github repository.
  If the parameter is omitted, set to null, or set to "default", the default value of
  **.../cloudscheduler/schema/schema_backup** is assumed. 
 
..

* **user_data_backup_dir** - specifies the full path of a local filesystem directory to be used as the
  user data backup directory. This directory may also be within a git/github repository, but it should
  be noted that this data contains private/senesitive information which should be kept secret.
  If the parameter is omitted, user data will not be backed up.

..

* **providers** - specifies a list of service names of services on the local host providing relational
  database services for CSV2. Normally, the list consists of one name, "mariadb" or possibly "mysql", 
  depending on your host configuration.

..

* **consumers** - specifies a list of service names of services that depend on the CSV2 database. Normally,
  this is a list of all CSV2 service components plus the web server. 

..

* **global** - specifies a list of tables names within the CSV2 database that comprise global configuration
  data. These tables do not contain any sensitive data.

..

* **local** - specifies a list of tables names within the CSV2 database that comprise user, group, and cloud
  configuration data. These tables will contain sensitive data.

..

* **ephemeral** - specifies a list of tables names within the CSV2 database that comprise the state of the
  distributed cloud system. This data is in a continual state of flux and is therefore never saved. However,
  the structure of the tables is important and is saved in the CSV2 backup directory.

..

* **ignore** - specifies a list of tables names within the CSV2 database used by other supporting services 
  and which can be ignored by schema_backup and other CSV2 utilities.

Any other parameter within the configuration file will be ignored.
