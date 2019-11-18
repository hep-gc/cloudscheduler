cloudscheduler
==============

.. toctree::
   :maxdepth: 1

   cloudscheduler_cloud



**NAME**
       
       **cloudscheduler**
       -  command  line  interface to cloudscheduler version 2
       (csv2) servers.


**SYNOPSIS**
       The general format of the 
       **cloudscheduler**
       command is as follows:

       
       **cloudscheduler**
       *object*
       *action*
       *mandatory_parameters*
       [
       *options*
       ...]


**DESCRIPTION**
       The 
       **cloudscheduler**
       command line interface  makes  RESTful  requests  to
       cloudscheduler  servers  to retrieve information and control batch pro-
       cessing on clouds.  It is an alternative to the web browser  interface,
       providing  the  same  functionality, and like the web browser interface
       can talk to any number of servers.

       CSV2 servers require authentication.  One of two methods of authentica-
       tion  must be used when communicating with servers; either username and
       password credentials, or an X509 certificate may be used.  Accounts and
       associated  credentials are set up by any privileged user, but any user
       can change their own password.

       The 
       **cloudscheduler**
       command provides the
       **defaults**
       object  together  with
       its'  associated  actions  to  manage  default  values for servers on a
       server by server basis.  Server location (URL), credential  parameters,
       mandatory  parameters,  and  other options are grouped under a "server"
       name.  The "default" server is always and automatically defined.

       Parameters come in two flavours, keyword/value  and  boolean.   Keyword
       parameters  have  no  default  value, whereas boolean values default to
       
       **False**.
       When a group of settings is saved for a server, it will contain
       all  the boolean values, but only those keywords that have been explic-
       itly set.  Specifying a boolean keyword more than once will toggle its'
       value  from  
       **False**
       to
       **True**
       and back to
       **False**,
       etc.  A default value can
       be saved in the 
       **defaults**
       but overridden on the command line.


**OBJECTS**
       The first two positional arguments to the  
       **cloudscheduler**
       command  are
       an  
       **object**
       and  an
       **action**
       to be perfomed.  For information about the
       actions associated with a particular object, refer to the documentation
       for  that  object  (eg.  
       **cloudscheduler**
       *object*
       **-H**).
       The following is a
       list and brief description of the available objects:

       
       **cloud**
       The
       **cloud**
       object adds, deletes, lists, modifies, and  shows  the
              status  of clouds within the current group.  For each group, one
              or more clouds, both commercial and  private,  can  be  defined.
              Defining  a  cloud  allows  cloudscheduler to manage the virtual
              machines(VMs) and condor job queue associated with  that  cloud.
              Each  cloud has an associated list of metadata files that can be
              modified using the 
              **metadata-**
              actions.   The  cloud  object  and
              actions  are  available  to  all users, provided they are in the
              group the cloud definitions belong to.

       
       **defaults**
              The 
              **defaults**
              object manipulates  groups  of  defaults  within  a
              user's  
              **~/.csv2**
              directory, and provides actions to set, delete,
              and list defaults for multiple servers.  A sub-directory is cre-
              ated  for  each  server, and within that sub-directory, a single
              
              **settings.yaml**
              file contains the default value for each parameter
              for  that server.  The defaults object and actions are available
              to all users.

       
       **group**
       The
       **group**
       object creates, lists, updates, and deletes groups  on
              
              **cloudscheduler**
              servers.   A group on a cloudscheduler server is
              analogous to a project on an OpenStack cloud and may have multi-
              ple  users,  anyone  of whom may control the cloud resources for
              the group.  Each group has an associated list of metadata  files
              that  can  be  modified  using the 
              **metadata-**
              actions.  The group
              object and actions  are  only  available  to  privileged  users.
              Unprivileged  users  may update group defaults and metadata with
              the 
              **cloudscheduler metadata**
              object.

       
       **helpers**
              This object provides functions to aid in the use  of  this  com-
              mand.


       
       **job**
       The
       **job**
       object lists jobs on csv2 servers.  The
       **job**
       object and
              actions are available to any users, provided  they  are  in  the
              group that the jobs belong to.

       
       **server**
       The
       **server**
       object  modifies and lists server configuration for
              
              **cloudscheduler**
              servers.  The server object and actions are  only
              available  to privileged users.  ***CAUTION: Modifing these val-
              ues can cause server errors***

       
       **user**
              The 
              **user**
              object adds, deletes, lists, and updates users on  csv2
              servers.   Each user can be assigned to groups, and will be able
              to manipulate the resources for the groups  to  which  they  are
              assigned.   The  
              **user**
              object  and actions are only available to
              privileged users.

              An unprivileged user will only be able to manage  the  defaults,
              metadata, clouds, jobs, and VMs that are in groups that they are
              a part of.  They will also be able to change their password.   A
              privileged  user, in addition to everything an unprivileged user
              can do, can also manage users and groups.

       
       **vm**
       The
       **vm**
       object lists and updates virtual  machines(VMs)  on  csv2
              servers.   The  
              **vm**
              object and actions are available to any user,
              provided the user is in the group that the VMs belong to.


**GLOBAL OPTIONS**
       The following global options are applicable to all 
       **cloudscheduler**
       com-
       mands:

   
   **Authentication Options**
       The following options are used to address the cloudscheduler server and
       to identify the user's current group to the server:

       
       **-sa**
       *url*,
       **--server-address**
       *url*
              Specifies the HTTPS  protocol  location  of  the  cloudscheduler
              server. The default URL is https://localhost.

       
       **-spw**
       *password*,
       **--server-password**
       *password*
              Specifies  the  password  to  use  when  authenticating with the
              cloudscheduler server.  If user/password authentication is being
              used  and  no  password  is  provided, a password prompt will be
              issued.

       
       **-su**
       *username*,
       **--server-user**
       *username*
              Specifies the user ID to use when authenticating with the cloud-
              scheduler  server.   If  specified, the user should also specify
              the 
              **-spw**
              option, or  a  password  promp  will  be  issued.   The
              default  is  to  attempt  X509 authentication; either your proxy
              certificate in "/tmp" or, failing that,  your  grid  certificate
              and key in your "~/.globus" directory.

       
       **-g**
       *group*,
       **--group**
       *group*
              Change  the  user's current group to 
              *group*.
              The
              *group*
              must exist
              and the current user must be in 
              *group*.

       
       **-s**
       *server*,
       **--server**
       *server*
              The name of the target server.  There must be an  entry  in  the
              
              **cloudscheduler  defaults**
              that matches
              *server*
              and it must have an
              authentication method.

   
   **Information Options**
       The following options are used to display  the  
       **cloudscheduler**
       command
       line interface and API documentation:

       
       **-h**,
       **--help**
              Requests  short  help  for  the  current  command.   Help can be
              requested for the 
              **cloudscheduler**
              command, a specific object,  or
              a specific object/action.

       
       **-H**,
       **-\-long-help**
              Requests  the man page style help for the current command.  Long
              help can be requested for the 
              **cloudscheduler**
              command, a specific
              object, or a specific object/action.

       
       **-v**,
       **--version**
              Requests  that  the versions of both the CLI client and the tar-
              geted server be printed in addition to any other command output.

       
       **-xA**,
       **--expose-API**
              Requests trace messages detailing the API  calls  and  responses
              issued and received by the 
              **cloudscheduler**
              command.


**SEE ALSO**
       
       **csv2_cloud**
       (1)
       **csv2_defaults**
       (1)
       **csv2_group**
       (1)
       **csv2_helpers**
       (1)
       
       **csv2_job**
       (1)
       **csv2_server**
       (1)
       **csv2_user**
       (1)
       **csv2_vm**
       (1)



cloudscheduler version 2        7 November 2018              cloudscheduler(1)
