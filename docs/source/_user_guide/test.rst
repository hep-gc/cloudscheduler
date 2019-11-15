cloudscheduler(1) General Commands Manual cloudscheduler(1)
===========================================================

[1mNAME[0m [1mcloudscheduler [22m- command line interface to
cloudscheduler version 2 (csv2) servers.

[1mSYNOPSIS[0m The general format of the [1mcloudscheduler
[22mcommand is as follows:

::

       [1mcloudscheduler [4m[22mobject[24m [4maction[24m [4mmandatory_parameters[24m [[4moptions[24m ...]

[1mDESCRIPTION[0m The [1mcloudscheduler [22mcommand line interface
makes RESTful requests to cloudscheduler servers to retrieve information
and control batch pro- cessing on clouds. It is an alternative to the
web browser interface, providing the same functionality, and like the
web browser interface can talk to any number of servers.

::

       CSV2 servers require authentication.  One of two methods of authentica-
       tion  must be used when communicating with servers; either username and
       password credentials, or an X509 certificate may be used.  Accounts and
       associated  credentials are set up by any privileged user, but any user
       can change their own password.

       The [1mcloudscheduler [22mcommand provides the [1mdefaults [22mobject  together  with
       its'  associated  actions  to  manage  default  values for servers on a
       server by server basis.  Server location (URL), credential  parameters,
       mandatory  parameters,  and  other options are grouped under a "server"
       name.  The "default" server is always and automatically defined.

       Parameters come in two flavours, keyword/value  and  boolean.   Keyword
       parameters  have  no  default  value, whereas boolean values default to
       [1mFalse[22m.  When a group of settings is saved for a server, it will contain
       all  the boolean values, but only those keywords that have been explic-
       itly set.  Specifying a boolean keyword more than once will toggle its'
       value  from  [1mFalse [22mto [1mTrue [22mand back to [1mFalse[22m, etc.  A default value can
       be saved in the [1mdefaults [22mbut overridden on the command line.

[1mOBJECTS[0m The first two positional arguments to the
[1mcloudscheduler [22mcommand are an [1mobject [22mand an [1maction
[22mto be perfomed. For information about the actions associated with a
particular object, refer to the documentation for that object (eg.
[1mcloudscheduler [4m[22mobject[24m [1m-H[22m). The following is a
list and brief description of the available objects:

::

       [1mcloud  [22mThe [1mcloud [22mobject adds, deletes, lists, modifies, and  shows  the
              status  of clouds within the current group.  For each group, one
              or more clouds, both commercial and  private,  can  be  defined.
              Defining  a  cloud  allows  cloudscheduler to manage the virtual
              machines(VMs) and condor job queue associated with  that  cloud.
              Each  cloud has an associated list of metadata files that can be
              modified using the [1mmetadata-  [22mactions.   The  cloud  object  and
              actions  are  available  to  all users, provided they are in the
              group the cloud definitions belong to.

       [1mdefaults[0m
              The [1mdefaults [22mobject manipulates  groups  of  defaults  within  a
              user's  [1m~/.csv2  [22mdirectory, and provides actions to set, delete,
              and list defaults for multiple servers.  A sub-directory is cre-
              ated  for  each  server, and within that sub-directory, a single
              [1msettings.yaml [22mfile contains the default value for each parameter
              for  that server.  The defaults object and actions are available
              to all users.

       [1mgroup  [22mThe [1mgroup [22mobject creates, lists, updates, and deletes groups  on
              [1mcloudscheduler  [22mservers.   A group on a cloudscheduler server is
              analogous to a project on an OpenStack cloud and may have multi-
              ple  users,  anyone  of whom may control the cloud resources for
              the group.  Each group has an associated list of metadata  files
              that  can  be  modified  using the [1mmetadata- [22mactions.  The group
              object and actions  are  only  available  to  privileged  users.
              Unprivileged  users  may update group defaults and metadata with
              the [1mcloudscheduler metadata [22mobject.

       [1mhelpers[0m
              This object provides functions to aid in the use  of  this  com-
              mand.


       [1mjob    [22mThe  [1mjob  [22mobject lists jobs on csv2 servers.  The [1mjob [22mobject and
              actions are available to any users, provided  they  are  in  the
              group that the jobs belong to.

       [1mserver [22mThe  [1mserver  [22mobject  modifies and lists server configuration for
              [1mcloudscheduler [22mservers.  The server object and actions are  only
              available  to privileged users.  ***CAUTION: Modifing these val-
              ues can cause server errors***

       [1muser[0m
              The [1muser [22mobject adds, deletes, lists, and updates users on  csv2
              servers.   Each user can be assigned to groups, and will be able
              to manipulate the resources for the groups  to  which  they  are
              assigned.   The  [1muser  [22mobject  and actions are only available to
              privileged users.

              An unprivileged user will only be able to manage  the  defaults,
              metadata, clouds, jobs, and VMs that are in groups that they are
              a part of.  They will also be able to change their password.   A
              privileged  user, in addition to everything an unprivileged user
              can do, can also manage users and groups.

       [1mvm     [22mThe [1mvm [22mobject lists and updates virtual  machines(VMs)  on  csv2
              servers.   The  [1mvm [22mobject and actions are available to any user,
              provided the user is in the group that the VMs belong to.

[1mGLOBAL OPTIONS[0m The following global options are applicable to
all [1mcloudscheduler [22mcom- mands:

[1mAuthentication Options[0m The following options are used to address
the cloudscheduler server and to identify the user's current group to
the server:

::

       [1m-sa [4m[22murl[24m, [1m--server-address [4m[22murl[0m
              Specifies the HTTPS  protocol  location  of  the  cloudscheduler
              server. The default URL is https://localhost.

       [1m-spw [4m[22mpassword[24m, [1m--server-password [4m[22mpassword[0m
              Specifies  the  password  to  use  when  authenticating with the
              cloudscheduler server.  If user/password authentication is being
              used  and  no  password  is  provided, a password prompt will be
              issued.

       [1m-su [4m[22musername[24m, [1m--server-user [4m[22musername[0m
              Specifies the user ID to use when authenticating with the cloud-
              scheduler  server.   If  specified, the user should also specify
              the [1m-spw [22moption, or  a  password  promp  will  be  issued.   The
              default  is  to  attempt  X509 authentication; either your proxy
              certificate in "/tmp" or, failing that,  your  grid  certificate
              and key in your "~/.globus" directory.

       [1m-g [4m[22mgroup[24m, [1m--group [4m[22mgroup[0m
              Change  the  user's current group to [4mgroup[24m. The [4mgroup[24m must exist
              and the current user must be in [4mgroup[24m.

       [1m-s [4m[22mserver[24m, [1m--server [4m[22mserver[0m
              The name of the target server.  There must be an  entry  in  the
              [1mcloudscheduler  defaults [22mthat matches [4mserver[24m and it must have an
              authentication method.

[1mInformation Options[0m The following options are used to display
the [1mcloudscheduler [22mcommand line interface and API
documentation:

::

       [1m-h[22m, [1m--help[0m
              Requests  short  help  for  the  current  command.   Help can be
              requested for the [1mcloudscheduler [22mcommand, a specific object,  or
              a specific object/action.

       [1m-H[22m, [1m--long-help[0m
              Requests  the man page style help for the current command.  Long
              help can be requested for the [1mcloudscheduler [22mcommand, a specific
              object, or a specific object/action.

       [1m-v[22m, [1m--version[0m
              Requests  that  the versions of both the CLI client and the tar-
              geted server be printed in addition to any other command output.

       [1m-xA[22m, [1m--expose-API[0m
              Requests trace messages detailing the API  calls  and  responses
              issued and received by the [1mcloudscheduler [22mcommand.

[1mSEE ALSO[0m [1mcsv2\_cloud[22m(1) [1mcsv2\_defaults[22m(1)
[1mcsv2\_group[22m(1) [1mcsv2\_helpers[22m(1) [1mcsv2\_job[22m(1)
[1mcsv2\_server[22m(1) [1mcsv2\_user[22m(1) [1mcsv2\_vm[22m(1)

cloudscheduler version 2 7 November 2018 cloudscheduler(1)
