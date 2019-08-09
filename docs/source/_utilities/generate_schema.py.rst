Utility: generate_schema.py
===========================

This utility is used during the development and the upgrade procedures to generate the schema mapping
file *.../cloudscheduler/lib/schema.py* used by other CSV2 processes that access the database.
The utility needs to be run each time there is a modification to the database schema, and processes
using the mapping file generated need to be restarted.

Synopsis: generate_schema.py

