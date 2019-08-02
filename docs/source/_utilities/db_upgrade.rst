Utility: db_upgrade
===================

The **db_upgrade** utility performs database schema updates during version changes by comparing 
the schema of the machine to be updated (target) with the upgraded schema (model).
The utility requires guidance when renaming tables and columns which is achieved either by
prompting interactively or by the specification of a batch control file. Batch control files, 
created when necessary during verion development, are distributed with the new version.

Synopsis: db_upgrade <model_dir> [-i <input_file_path>] [-o <output_file_path>] [-r live | ]

Where:

* <model_dir>

   * is the name of a directory in *.../cloudscheduler/schema/schema_backup*
     containing a database backup to be used as a schema model.

* -i <input_file_name> 

   * is the name of an optional input parameter file, located within
     ".../cloudscheduler/schema/db_upgrade", used to automate the
     database upgrade process. Normally, based on table and column names,
     db_upgrade is able to make the target database match the structure
     and format of the model database. However, when tables or columns are
     either added or deleted or renamed, user input is required to resolve
     the discrepencies. This input can either be read interactively from
     the terminal or from this parameter file.

* -o <output_file_name> 

   * is the name of an optional output parameter file used to record the
     users responses for future automation of the upgrade process (see
     the "-i" option above). The output file is written to the directory
     ".../cloudscheduler/schema/db_upgrade".

* -r [live | ]

   * The "-r" specifies the run mode and is either "live" or anything else
     (default). Changes to the target database are only made if the run mode
     is "live".


When called with the "-r live" option, **db_upgrade** proceeds as follows:

#. Calls **schema_backup** to save a copy of the old schema.
#. Redefines all global configuration tables and populates them with values from the model.
#. Updates all global configuration tables with values ifrom the target which have been modified locally.
#. Maps the structure of local configuration and ephemeral tables
#. Scans local configuration and ephemeral maps for tables to add, ignore or rename.
#. Prints a summary of new or missing tables.
#. Ignores or renames tables not in the model.
#. Adds model tables that are not already in the target.
#. Scans for columns to add, ignore or rename.
#. Adds, ignores or renames target columns that are not already in the model.'
#. Loads local configuration data.
#. Redefines all views and triggers.
#. Calls **generate_schema.py.rst** to regenerate the schema definition library code  
   used by other CSV2 services to map the structure of the database.

