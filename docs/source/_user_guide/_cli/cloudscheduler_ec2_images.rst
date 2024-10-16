.. File generated by /hepuser/crlb/Git/cloudscheduler/utilities/cli_doc_to_rst - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the man page file(s) ".../cloudscheduler/cli/man/csv2_ec2_images.1"
..   2. run the utility ".../cloudscheduler/utilities/cli_doc_to_rst"
..

man(1) page: cloudscheduler ec2 images
======================================

 
 
 
**NAME**  
       **cloudscheduler  ec2  images** 
       -  filter  and  list EC2 images to be made 
       available to cloudscheduler version 2 (csv2).
 
**SYNOPSIS**  
       **cloudscheduler ec2 images** 
       [ *options*
       ...] 
 
**DESCRIPTION**  
       Amazon EC2 offers a vast collection  of  Virtual  Machine  (VM)  images
       available  for  excution.   In addition to the public images offered by
       Amazon, any user can create and upload images, make them public,  share
       them  with other specific users, or keep them for private use.  With so
       many images to choose from, the  process  of  image  selection  can  be
       rather  daunting.   The **ec2 images** 
       function of cloudscheduler version 2 
       (CSV2) provides a filtering system  to  ease  the  problem  of  finding
       appropriate  images  and  reduce the overhead of managing the images of
       interest.   Since  different  images  may  be  available  to  different
       regions,  filtering  is  performed  on  a  cloud by cloud basis.  It is
       therefore necessary to specify from which cloud connection  the  images
       are to be viewed.
 
**OPTIONS**  
   **Mandatory**  
       The following are mandatory parameters and must be specified:
 
       **-cn** *name*,  **\\-\\-cloud-name** *name* 
              A  cloud  name.   The  value  for *name*
              must be one to thirty-two 
              characters, all lower case, numeric digits, and dashes but  
              cannot start or end with dashes.
 
   **Optional**  
       Optional  parameters  are  used to modify the filters for the specified
       cloud.
 
       The following are optional parameters:
 
       **-ia** *arch1*
       [,arch2,... archN], **\\-\\-ec2-image-architectures** *arch1*
       [,arch2,... 
       archN]
              Specifies  a  comma-seperated list of architectures of interest.
              Valid architectures are displayed in the **Architectures** 
              optional 
              table  (see  **cloudscheduler  -H** , 
              the **\\-\\-with** 
              clause).  The **ec2**  
              object is to filter out images with an architecture  other  than
              specified by this parameter.
 
              Default: (defined in the system configuration)
 
       **-il** *string1*
       [,string2,...        stringN], **\\-\\-ec2-image-like**  
       *string1*
       [,string2,... stringN] 
              Specifies a  comma-seperated  list  of  strings  to  be  matched
              against  the  images  location.   Images  whose  location  match
              string1 **and** 
              string2 **and** 
              etc.  are  considered  of  interest  and 
              included  in the list.  All other images will be filtered out by
              the ec2 object.
 
              Why match the image location? Unlike  the  image  name  and  the
              image  description, the image location is mandatory and normally
              reflects what the image is.
 
              Default: None.
 
       **-inl** *string1*
       [,string2,...      stringN], **\\-\\-ec2-image-not-like**  
       *string1*
       [,string2,... stringN] 
              Specifies  a comma-seperated list of strings that must not match
              the image location.  Images  whose  location  match  string1  **or**  
              string2  **or** 
              etc.  are  to  be excluded from the list by the ec2 
              object.
 
              Default: None.
 
       **-ioa** *alias1*
       [,alias2,...     aliasN], **\\-\\-ec2-image-owner-aliases**  
       *alias1*
       [,alias2,... aliasN] 
              Specifies  a  comma-seperated list of owner aliases of interest.
              The **ec2** 
              object is to filter out images belonging to owners other 
              than  specified  by  this parameter or the **\\-\\-ec2-image-owner-ids**  
              parameter.
 
              Unlike other filters, this parameter and the  **\\-\\-ec2-image-owner-**  
              **ids** 
              parameter also determine what is retrieved from Amazon EC2. 
              Because there are so many  images  (millions?)  available,  only
              images belonging to the owners identified are retrieved.
 
              The  special  aliases  of  "self"  (images belonging to you) and
              "shared" (images specifically shared with you by  someone  else)
              are recommeded.
 
              Default: (defined in the system configuration).
 
       **-ioi** *id1*
       [,id2,... idN], **\\-\\-ec2-image-owner-ids** *id1*
       [,id2,... idN] 
              Specifies  a comma-seperated list of owner IDs of interest.  The
              **ec2** 
              object is to filter out images  belonging  to  owners  other 
              than  specified  by  this  parameter  or  the **\\-\\-ec2-image-owner-**  
              **aliases** 
              parameter. 
 
              Unlike other filters, this parameter and the  **\\-\\-ec2-image-owner-**  
              **aliases** 
              parameter  also determine what is retrieved from Amazon 
              EC2. Because there are so  many  images  (millions?)  available,
              only images belonging to the owners identified are retrieved.
 
              Default: (defined in the system configuration).
 
       **-ios** *os1*
       [,os2,... osN], **\\-\\-ec2-image-operating-systems** *os1*
       [,os2,... osN] 
              Specifies  a comma-seperated list of operating systems of 
              interest.  Valid operating systems are  displayed  in  the  **Operating**  
              **Systems** 
              optional table (see **\\-\\-with** 
              below).  The **ec2** 
              object is to 
              filter out images with an operating system other than  specified
              by this parameter.
 
              Default: (defined in the system configuration)
 
   **Table**  
       These options change the format of the displayed table(s):
 
       **-CSV** *column1*
       [,column2,...   columnN], **\\-\\-comma-separated-values** *col-* 
       *umn1*
       [,column2,... columnN] 
              Requests that a list of  comma  separated  values  be  displayed
              instead  of  tabular output.  Only the specified columns will be
              displayed from the current view (see **\\-\\-view** ). 
              To  display  all 
              columns  from  the  current  view,  specify  a  null string, ie.
              "--comma-separated-values ''".
 
 
       **-CSEP** *separator*,  **\\-\\-comma-separated-values-separator** *separator* 
              Specifies the column separator character to be used by the  -CSV
              parameter  when  printing the result.  By default, a comma (",")
              is used.
 
 
       **-NV** ,  **\\-\\-no-view**  
              Ignores any defined view (see **\\-\\-view** 
              ) for this invocation of the 
              command.  All columns present in the list will be displayed.
 
       **-ok** ,  **\\-\\-only-keys**  
              Only  displays  the  values  of the keys in this list.  No other
              columns are displayed.
 
       **-r** ,  **\\-\\-rotate**  
              Rotate the listed table to only have a **Key** 
              and a **Value** 
              column. 
              Used to improve readability of tables with many columns.
 
       **-V** *column1*
       [,column2,... columnN], **\\-\\-view** *column1*
       [,column2,... columnN] 
              Specifies a comma-seperated list of table column names which are
              to be displayed.  All other columns will be ignored.  For a 
              command  that produces multiple result tables, the column name list
              for each table is separated by a slash (**/** ). 
              Using this 
              parameter  defines a "view" for this and all subsequent invocations of
              this command; the same column selections will be displayed until
              the "view" is redefined by the **\\-\\-view** 
              option.  To remove a view, 
              specify a null string, ie.  "--with  ''",  in  which  case,  all
              defined columns will be displayed.  To see which tables and 
              columns that can be displayed, use the **\\-\\-view-columns** 
              option. 
 
              Default: None.
 
       **-VC** ,  **\\-\\-view-columns**  
              View all table and column names associated  with  this  command.
              For  each  table of information returned by the command, a table
              number, table name, a possible "optional" designation, the "key"
              column  (those that are displayed at the beginning of every 
              segment) names, and all remaining column names are displayed.  This
              information  is  useful when creating views (see **\\-\\-view** 
              ) or when 
              selecting columns for comma separated output (see  **\\-\\-comma-sepa-**  
              **rated-values** ).  
 
       **-w** *table1*
       [,table2,... tableN], **\\-\\-with** *table1*
       [,table2,... tableN] 
              Specifies  a comma-seperated list of names of optional tables to
              be displayed.   Some  commands  provide  additional  information
              which  are  not displayed unless specifically requested by name.
              To determine the information returned by any particular command,
              use the **\\-\\-view-columns** 
              ( **-VC** 
              ) option which provides a list of 
              table numbers, tables names, and columns,  high-lighting  optional
              information.   This  option  accepts  table  numbers  as well as
              tables names and the special value of **ALL** 
              which will display all 
              optional information.
 
              Default: None.
 
   **Global**  
       These   options   are   avaliable  on  all  actions:.so  
       ../man/parameters/_group.so
 
       **-H** ,  **\\-\\-long-help**  
              Requests the man page style help for the current command.   Long
              help can be requested for the **cloudscheduler** 
              command, a specific 
              object, or a specific object/action.
 
       **-h** ,  **\\-\\-help**  
              Requests short help  for  the  current  command.   Help  can  be
              requested  for the **cloudscheduler** 
              command, a specific object, or 
              a specific object/action.
 
       **-s** *server*,  **\\-\\-server** *server* 
              The name of the target server.  There must be an  entry  in  the
              **cloudscheduler  defaults** 
              that matches *server*
              and it must have an 
              authentication method.
 
       **-v** ,  **\\-\\-version**  
              Requests that the versions of both the CLI client and  the  
              targeted server be printed in addition to any other command output.
 
       **-xA** ,  **\\-\\-expose-API**  
              Requests  trace  messages  detailing the API calls and responses
              issued and received by the **cloudscheduler** 
              command. 
 
**EXAMPLES**  
       1.     View EC2 image filters and images together with optional  tables
              **Architecture Filter** 
              and **Owner Alias Filter** 
              : 
 
              $ cloudscheduler ec2 images -cn amazon-east --with owner,arch
              Server: dev, Active User: crlb, Active Group: testing, User's Groups: ['crlb', 'demo', 'test', 'test-dev2', 'testing']
 
              EC2 Image Filters:

              +---------+-------------+-------------+--------------+--------+----------+-------------------+---------------+
              +         |             |           Owner            |      Images       |                   |               +
              +  Group  |    Cloud    |   Aliases         IDs      |  Like    Not Like | Operating Systems | Architectures +
              +=========+=============+=============+==============+========+==========+===================+===============+
              | testing | amazon-east | self,shared | 206029621532 | None   | None     | linux             | 32bit         |
              +---------+-------------+-------------+--------------+--------+----------+-------------------+---------------+

              Rows: 1
 
              Architecture Filter:

              +--------------+
              + Architecture +
              +==============+
              | 32bit        |
              | 64bit        |
              | arm64        |
              | xml          |
              +--------------+

              Rows: 4
 
              Owner Alias Filter:

              +-----------+
              + Alias     +
              +===========+
              | amazon    |
              | microsoft |
              | self      |
              | shared    |
              +-----------+

              Rows: 4
 
              EC2 Images:

              +-----------+----------------------------------------+--------------+--------+--------------+-------------+------------------+--------------+-------------+-------------+------------+--------------+
              +           |                                        |              |         Owner         |             |                  |              |             |             |            |              +
              +  Region   |                Location                |      ID      | Alias         ID      | Borrower ID | Operating System | Architecture | Disk Fromat |    Size     | Visibility | Last Updated +
              +===========+========================================+==============+========+==============+=============+==================+==============+=============+=============+============+==============+
              | us-east-1 | amazon/ami-vpc-nat-1.1.0-beta.i386-ebs | ami-2e1bc047 | amazon | 206029621532 | not_shared  | linux            | 32bit        | ebs         | 8           | 1          | 1557784233   |
              | us-east-1 | amazon/fedora-8-i386-v1.14-std         | ami-84db39ed | amazon | 206029621532 | not_shared  | linux            | 32bit        | ebs         | 15          | 1          | 1557784233   |
              | us-east-1 | amazon/ami-vpc-nat-1.0.0-beta.i386-ebs | ami-d8699bb1 | amazon | 206029621532 | not_shared  | linux            | 32bit        | ebs         | 8           | 1          | 1557784233   |
              +-----------+----------------------------------------+--------------+--------+--------------+-------------+------------------+--------------+-------------+-------------+------------+--------------+

              Rows: 3
              $
 
       2.     Update  the filter to list 64 bit images (**\\-\\-image-architetures** ),  
              include  Amazon  public  images  (**\\-\\-imager-owner-aliases** ), 
              and 
              select only the latest SUSE distribution images (**\\-\\-image-like** 
              ): 
 
              $ cloudscheduler ec2 images -cn amazon-east -ia 64bit -ioa amazon,self,shared -il suse-sles-12-sp4
              Server: dev, Active User: crlb, Active Group: testing, User's Groups: ['crlb', 'demo', 'test', 'test-dev2', 'testing']
 
              EC2 Image Filters:

              +---------+-------------+--------------------+--------------+------------------+----------+-------------------+---------------+
              +         |             |               Owner               |           Images            |                   |               +
              +  Group  |    Cloud    |      Aliases             IDs      |       Like         Not Like | Operating Systems | Architectures +
              +=========+=============+====================+==============+==================+==========+===================+===============+
              | testing | amazon-east | amazon,self,shared | 206029621532 | suse-sles-12-sp4 | None     | linux             | 64bit         |
              +---------+-------------+--------------------+--------------+------------------+----------+-------------------+---------------+

              Rows: 1
 
              EC2 Images:

              +-----------+-------------------------------------------------------+-----------------------+--------+--------------+-------------+------------------+--------------+-------------+-------------+------------+--------------+
              +           |                                                       |                       |         Owner         |             |                  |              |             |             |            |              +
              +  Region   |                       Location                        |          ID           | Alias         ID      | Borrower ID | Operating System | Architecture | Disk Fromat |    Size     | Visibility | Last Updated +
              +===========+=======================================================+=======================+========+==============+=============+==================+==============+=============+=============+============+==============+
              | us-east-1 | amazon/suse-sles-12-sp4-byos-v20190314-hvm-ssd-x86_64 | ami-016ddc817bedb3d8e | amazon | 013907871322 | not_shared  | linux            | 64bit        | ebs         | 10          | 1          | 1557784233   |
              | us-east-1 | amazon/suse-sles-12-sp4-v20190314-ecs-hvm-ssd-x86_64  | ami-0295228f2225d55a9 | amazon | 013907871322 | not_shared  | linux            | 64bit        | ebs         | 10          | 1          | 1557784233   |
              | us-east-1 | amazon/suse-sles-12-sp4-v20190314-hvm-ssd-x86_64      | ami-0787571b4033204ad | amazon | 013907871322 | not_shared  | linux            | 64bit        | ebs         | 10          | 1          | 1557784233   |
              | us-east-1 | amazon/suse-sles-12-sp4-byos-v20181212-hvm-ssd-x86_64 | ami-0ba0b96806bf03d31 | amazon | 013907871322 | not_shared  | linux            | 64bit        | ebs         | 10          | 1          | 1557784233   |
              | us-east-1 | amazon/suse-sles-12-sp4-v20181212-hvm-ssd-x86_64      | ami-0c55353c85ac52c96 | amazon | 013907871322 | not_shared  | linux            | 64bit        | ebs         | 10          | 1          | 1557784233   |
              | us-east-1 | amazon/suse-sles-12-sp4-v20181212-ecs-hvm-ssd-x86_64  | ami-0cc46b3d7956578d4 | amazon | 013907871322 | not_shared  | linux            | 64bit        | ebs         | 10          | 1          | 1557784233   |
              +-----------+-------------------------------------------------------+-----------------------+--------+--------------+-------------+------------------+--------------+-------------+-------------+------------+--------------+

              Rows: 6
              $
 
**SEE ALSO**  
       **csv2** 
       (1) **csv2_ec2** 
       (1) **csv2_ec2_instance_types** 
       (1) 
 
 
 
cloudscheduler version 2        7 November 2018              cloudscheduler(1)
 

.. note:: The results of an SQL query will be formatted differently from the Restructured Text tables shown above.
