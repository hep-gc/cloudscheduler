.. File generated by /hepuser/crlb/Git/cloudscheduler/utilities/cli_doc_to_rst - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the man page file(s) ".../cloudscheduler/cli/man/csv2_user_delete.1"
..   2. run the utility ".../cloudscheduler/utilities/cli_doc_to_rst"
..

man(1) page: cloudscheduler user delete
=======================================

 
 
 
**NAME**  
       **cloudscheduler user delete** 
       - delete users from cloudscheduler version 2 
       (csv2) servers
 
**SYNOPSIS**  
       **cloudscheduler user delete -un** *username*
       [ *options*
       ...] 
 
**DESCRIPTION**  
       The **cloudscheduler user delete** 
       action deletes users from csv2  servers. 
       The  deleted user will be removed from all groups and will no longer be
       able to access the csv2 server.  This action is only available to 
       privileged users.
 
**OPTIONS**  
   **Mandatory**  
       The following are mandatory parameters and must be specified:
 
       **-un** *username*,  **\\-\\-username** *username* 
              The username of the user to be deleted. If there is no user with
              *username*
              an error is returned. 
 
   **Optional**  
       The following are optional parameters:
 
       **-Y** ,  **\\-\\-yes**  
              Specify this option to automatically accept  the  deletion.   If
              not  specified  a  prompt will appear asking if the user is sure
              they would like to delete the object..
 
   **Global**  
       These  options  are  avaliable  on   all   actions:.so   
       ../man/parameters/_group.so
 
       **-H** ,  **\\-\\-long-help**  
              Requests  the man page style help for the current command.  Long
              help can be requested for the **cloudscheduler** 
              command, a specific 
              object, or a specific object/action.
 
       **-h** ,  **\\-\\-help**  
              Requests  short  help  for  the  current  command.   Help can be
              requested for the **cloudscheduler** 
              command, a specific object,  or 
              a specific object/action.
 
       **-s** *server*,  **\\-\\-server** *server* 
              The  name  of  the target server.  There must be an entry in the
              **cloudscheduler defaults** 
              that matches *server*
              and it must have  an 
              authentication method.
 
       **-v** ,  **\\-\\-version**  
              Requests  that  the versions of both the CLI client and the 
              targeted server be printed in addition to any other command output.
 
       **-xA** ,  **\\-\\-expose-API**  
              Requests trace messages detailing the API  calls  and  responses
              issued and received by the **cloudscheduler** 
              command. 
 
**EXAMPLES**  
       1.     Deleting the user "example":
              $ cloudscheduler user delete -un example
              Are you sure you want to delete user "example"? (yes|..)
              yes
              user "example" successfully deleted.
 
**SEE ALSO**  
       **csv2** 
       (1) **csv2_user** 
       (1) **csv2_user_add** 
       (1) **csv2_user_list** 
       (1) 
       **csv2_user_update** 
       (1) 
 
 
 
cloudscheduler version 2        7 November 2018              cloudscheduler(1)
 
