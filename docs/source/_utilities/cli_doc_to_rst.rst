Utility: cli_doc_to_rst
=======================

cli_doc_to_rst converts the cloudscheduler man page files within the directory *.../cloudscheduler/cli/man*
to restructured text files saved within the directory *.../cloudscheduler/docs/source/_user_guids_cli*.
The converted files are used by the **readthedocs** web service to present the the cloudscheduler 
man pages.

Additionally, when converting files, the cli_doc_to_rst utility issues warning messages for any missing
man pages and can therefore be used by developers to check for incomplete documentation.

Synopsis: cli_doc_to_rst

