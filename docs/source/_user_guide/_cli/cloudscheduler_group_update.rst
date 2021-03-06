.. File generated by /hepuser/crlb/Git/cloudscheduler/utilities/cli_doc_to_rst - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the man page file(s) ".../cloudscheduler/cli/man/csv2_group_update.1"
..   2. run the utility ".../cloudscheduler/utilities/cli_doc_to_rst"
..

man(1) page: cloudscheduler group update
========================================

 
 
 
**NAME**  
       **cloudscheduler group update** 
       - modify groups on cloudscheduler version 2 
       (csv2) servers
 
**SYNOPSIS**  
       **cloudscheduler group update -gn** *name*
       [ *options*
       ...] 
 
**DESCRIPTION**  
       The **cloudscheduler group update** 
       action modifies groups on csv2 servers. 
       This action is only available to privileged users.
 
 
**OPTIONS**  
   **Mandatory**  
       The following are mandatory parameters and must be specified:
 
       **-gn** *name*,  **\\-\\-group-name** *name* 
              The  group  name.   The value for *name*
              must be one to thirty-two 
              characters, all lower case, numeric digits, and dashes but  
              cannot start or end with dashes.
 
   **Optional**  
       The following are optional parameters:
 
       **-gm** *manager*,  **\\-\\-group-manager** *manager* 
              The  hostname  of the machine where the Condor Collector is 
              running.
 
       **-un** *user*
       [,...], **\\-\\-username** *user*
       [,...] 
              The users to add or delete from the group, where *user*
              is a comma 
              seperated list of existing usernames.
 
 
       **-uo** 
       [ **add** 
       | **delete** 
       ], **\\-\\-user-option** 
       [ **add** 
       | **delete** 
       ] 
              Use  with  **-un** 
              to **add** 
              or **delete** 
              users from the group.  If this 
              command is not specified the default behavoir is **add** . 
              If **add** 
              is 
              specified  then the users will be added to the group.  If **delete**  
              is specified then the users will be removed from the group.
 
 
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
       1.     Updating the group "example":
              $ cloudscheduler group update -gn example -gm example.ca
              group "example" successfully updated.
 
       2.     Adding users to the group "example":
              $ cloudscheduler group update -gn example -un user1,user2
              group "example" successfully updated.
 
       3.     Removing users from the group "example":
              $ cloudscheduler group update -gn example -un user1,user2 -uo delete
              group "example" successfully updated.
 
**SEE ALSO**  
       **csv2** 
       (1) **csv2_group** 
       (1) **csv2_group_add** 
       (1) **csv2_group_defaults** 
       (1) 
       **csv2_group_delete** 
       (1) **csv2_group_list** 
       (1) **csv2_group_metadata-delete** 
       (1) 
       **csv2_group_metadata-edit** 
       (1) **csv2_group_metadata-list** 
       (1) 
       **csv2_group_metadata-load** 
       (1) **csv2_group_metadata-update** 
       (1) 
 
 
 
 
cloudscheduler version 2        7 November 2018              cloudscheduler(1)
 
