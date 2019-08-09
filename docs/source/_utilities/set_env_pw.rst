Utility: set_env_pw
===================

This bash script is provided to allow authorized user secure and easier access to the database.
It reads the CSV2 configuration file */etc/cloudscheduler/cloudscheduler.yaml* and creates the
shell environment variable **pw** containing CSV2's database password. Subsequently, the user
may access the database with the following::

    mysql -u csv2 -p$pw csv2 ...

Synopsis: . set_env_pw

