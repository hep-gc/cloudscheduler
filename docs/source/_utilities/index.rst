Utilities
=========

The utilities provided in the directory ".../cloudscheduler/utilities" provide functions
to manage and monitor CSV2 development and operations. With the exception of one utility,
**reset_stand_alone_hostname**, each require access to the CSV2 configuration file. This
can be achieved by assigning "cloudscheduler" as a secondary group to authorized users,
or by granting sudo privileges.

The utilities can be divided into two categories:

.. toctree::
   :maxdepth: 1
   :caption: Utilities for Development and Maintenance:

   cli_doc_to_rst
   cstrigger
   csview
   db_upgrade
   generate_schema.py
   regenerate_ansible_playbook
   schema_doc

.. toctree::
   :maxdepth: 1
   :caption: Utilities for Operations

   reset_stand_alone_hostname
   schema_backup
   set_env_pw
   watch_csv2

