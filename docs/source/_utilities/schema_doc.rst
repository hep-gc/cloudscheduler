Utility: schema_doc
===================

This utility generates Restructured Text files to document the CSV2 database schema
for the **readthedocs** web service.
Information about the database schema is held in three places:

#. The schema within the database.
#. The schema backup configuration file (**.../cloudscheduler/etc/schema_backup.conf**).
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
       
This text would be rendered into a python dictionary as one long string as follows::

   a_text_dictionary['Synopsis'] = 'This is paragraph one. It is not a very' \
                                   'long paragraph but it is longer than' \
                                   'paragraph two.\nThis is paragraph two.'

Note how the conversion retains only one new line character and drops all unnecessary white space. This is
problematic because RST depends on new lines and white space to indicate the text formatting.

The **schema_doc** utility provides two methods for handling text from YAML files:

#. Unformated text.
#. RST formated text.

Unformatted text
----------------

In the case of unformatted text, as in the YAML example above, **schema_doc** splits the text at new
line characters into paragraphs and then splits the paragraphs into words eliminating white space. It
then generates restructured text, preserving the paragraph structure, with twelve words per line, and
with appropriate indentation for either table/view descriptions or for key/column descriptions. Assuming
the YAML example above is a description of a table, the following restructured text would be produced::

   This is paragragh one. It is not a very long paragragh but
   it is longer than paragraph two.

   This is paragragh two.

If the YAML example above is a description for a string column named 'yaml_to_rst_example', information
about the column would be retrieved from the database and combined with the description to produce the
following restructured text::

   * **yaml_to_rst_example** (String(32)):

         This is paragragh one. It is not a very long paragragh but
         it is longer than paragraph two.

         This is paragragh two.

RST formatted text
------------------

In the case of RST formatted text, it is important to preserve new line characters and white space
to achieve the appropriate text formatting. The **schema_doc** utiity recognizes backslash ('\\\\') 
characters embedded within the text as psuedo new line characters, and the presence of psuedo new
line characters in the text indicates RST formatted text. In regard to white space, the YAML to 
python dictionary conversion will not preserve any white space at the beginning or the end of any
line of text, but it will preserve any white space imbedded within a line of text. With these two
features, we can now encapsulate restructured text within a YAML file. For example, the following
restructured text::

   This is my two paragraph title
   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   This is paragragh one. It is not a very long paragragh but it
   is longer than paragraph two and it has a couple of bullets
   and sub-bullets:
   
   * Bullet 1.

      #. numbered sub-bullet 1.

      #. numbered sub-bullet 2.
   
   * Bullet 2..

   This is paragragh two.

Could be encapsulated in a YAML text string as follows::

   This is my two paragraph title\\
   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   This is paragragh one. It is not a very long paragragh but it
   is longer than paragraph two and it has a couple of bullets
   and sub-bullets:
   
   * Bullet 1.

   \\   #. numbered sub-bullet 1.

   \\   #. numbered sub-bullet 2.
   
   * Bullet 2..

   This is paragragh two.

Note the format and position of the psuedo new line characters. The double backslash is
required because a backslash is a YAML escape character that would be lost during the 
YAML to python conversion. In the case of the first psuedo line end character in the
example above, no white space needs to be preserved and so it is safe to place it at 
the end of the first of the two title lines. In the case of the second and third psuedo
line end characters, the white space before the hash ('#') characters is important and
so they are placed at the begining of the line.

The rendering of this example on **readthedocs** is as follows:

This is my two paragraph title
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is paragragh one. It is not a very long paragragh but it
is longer than paragraph two and it has a couple of bullets
and sub-bullets:

* Bullet 1.

   #. numbered sub-bullet 1.

   #. numbered sub-bullet 2.

* Bullet 2..

This is paragragh two.

Text References
^^^^^^^^^^^^^^^

Because some database columns, eg. group_name, cloud_name, etc., can be repeated in many
different tables, and the synopsis for these fields is often repetitive, the **schema_doc**
utility supports the referencing (and copying) of previosly defined text. This allows a common
piece of text to be defined in one place but used in many other places; the reference to a
text is replaced by the text being referenced.

Synopsis can contain contain reference strings in the following forms:

* REF=(common/<file_name>)
* REF=(common/<file_name>/Keys/<key_name>)
* REF=(common/<file_name>/Columns/<col_name>)
* REF=(tables/<table_name>)
* REF=(tables/<table_name>/Keys/<key_name>)
* REF=(tables/<table_name>/Columns/<col_name>)
* REF=(views/<view_name>)
* REF=(views/<view_name>/Keys/<key_name>)
* REF=(views/<view_name>/Columns/<col_name>)

Each of these reference (note the case of 'Keys' and 'Columns' which is significant) points to
a synopsis location. Since synopsis can support one or more paragraphs, each of these references
can be qualified with:

   /N

Where N is the index of the paragraph that is being referenced (as opposed to 
the whole synopsis), for example::

   REF=(tables/<table_name>/Columns/<col_name>/N)

