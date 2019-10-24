Utility: schema_doc
===================

Database schema documentation is maintained via the **schema_doc** utility.  
Information about the schema is held in three places:

#. The schema within the database.
#. The schema backup configuration file (*.../cloudscheduler/etc/schema_backup.conf*).
#. The yaml and template .rst files within the **.../cloudscheduler/docs/schema_doc** documentation directory.

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

YAML vs RST Text Formatting
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The descriptive information for tables, views, keys, and columns is held within yaml files, one file for each
table or view. This arrangement allows for a piece of text to be correctly and easily associated with the 
particular object it is describing. However, this choice of YAML for the text repository does present some
text formatting challenges since the information must be rendered in Restructured Text (RST) format for the
**readthedocs** web service.

Consider the following YAML file entry::

   Synopsis:
       This is paragragh one.
       It is not a very long paragragh but it is longer than paragraph two.

       This is paragragh two.
       
This text would be rendered would be rendered to a python dictionary as follows::

   a_text_dictionary['Synopsis'] = 'This is paragraph one. It is not a very' \
                                   'long paragraph but it is longer than' \
                                   'paragraph two.\nThis is paragraph two.'

Note how the conversion retains only one new line character and drops all unnecessary white space. This is
problematic because RST depends on new lines and white space to indicate the required formatting.

The **schema_doc** utility provides two methods for handling text from YAML files:

#. Unformated text.
#. RST formated text.

Unformatted text
----------------

In the case of unformatted text, as in the YAML example above, **schema_doc** splits the text at new
line characters into paragraphs and then splits the paragraphs into words eliminating white space. It
then generates restructured text, preserving the paragraph structure, with twelve words per line, and
with appropriate indentation for either table/view descriptions or for key/column descriptions. Assuming
the YAML example above is a descript for a string column named 'yaml_to_rst_example', the following
restructured text would be produced::

* **yaml_to_rst_example** (String(32)):

      This is paragragh one. It is not a very long paragragh but
      it is longer than paragraph two.

       This is paragragh two.

RST formatted text
----------------

xxxxx

