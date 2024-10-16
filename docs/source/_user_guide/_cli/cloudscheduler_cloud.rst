.. File generated by /hepuser/crlb/Git/cloudscheduler/utilities/cli_doc_to_rst - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the man page file(s) ".../cloudscheduler/cli/man/csv2_cloud.1"
..   2. run the utility ".../cloudscheduler/utilities/cli_doc_to_rst"
..

man(1) page: cloudscheduler cloud
=================================

 
 
 
**NAME**  
       **cloudscheduler cloud** 
       - manage clouds on cloudscheduler version 2 (csv2) 
       servers
 
**SYNOPSIS**  
       **cloudscheduler cloud** *action* *mandatory_parameters*
       [ *options*
       ...] 
 
**DESCRIPTION**  
       The **cloud** 
       object adds, deletes, lists, modifies, and shows  the  status 
       of  clouds  within  the  current  group.   For  each group, one or more
       clouds, both commercial and private, can be defined.  Defining a  cloud
       allows  cloudscheduler  to  manage the virtual machines(VMs) and condor
       job queue associated with that cloud.  Each  cloud  has  an  associated
       list  of  metadata  files  that  can  be  modified  using the **metadata-**  
       actions.  The cloud object and actions are available to all users, 
       provided they are in the group the cloud definitions belong to.
 
**ACTIONS**  
       For  information  on  the parameters associated with each **cloud** 
       action, 
       refer to the documentation for that action (**cloudscheduler cloud** *action* 
       **-H** ). 
       The following actions are available for the **cloud** 
       object: 
 
       **add** 
       Adds  a  new cloud definition to the current group.  A group may 
              have multiple cloud definitions.  Any user may add a cloud 
              definition,  provided they are in the group that they are adding the
              cloud definition to.
 
       **delete** 
       Removes a cloud definition from the current group.  Any user may 
              delete  a  cloud definition, provided they are in the group that
              they are deleteing the cloud definition from.  ***PLANNED: If  a
              cloud has running jobs or VMs the delete will fail.***
 
       **list** 
       Lists  all  the  cloud  definitions  for the current group.  Any 
              metadata filename lists in this table are in  alphabetic  order,
              to  see  the  priority  ordering use the command: **cloudscheduler**  
              **cloud metadata-list** 
              or **cloudscheduler cloud  metadata-collation** .  
              Any  user  may  list the cloud definitions, provided they are in
              the group that they are listing the clouds for.
 
       **metadata-collation**  
              Collate the list of metadata from the group  with  the  metadata
              list  of  a  specific cloud.  This list is all the metadata that
              will be applied to a VM started on that  cloud.   Any  user  may
              collate  a  clouds metadata, provided that they are in the group
              that they are collating the metadata for.
 
       **metadata-delete**  
              Remove metadata files from a cloud in the  current  group.   Any
              user  may  delete cloud metadata files, provided they are in the
              group that the cloud is defined in.
 
       **metadata-edit**  
              Edit a cloud metadata file in the current group.   The  metadata
              file is fetched from the server and edited locally.  On 
              successfully saving changes the server copy is  updated  to  match  the
              changed file.  Any user may edit a cloud metadata file, provided
              they are in the group that the cloud is defined in.
 
       **metadata-list**  
              List the cloud metadata for the current  group.   Any  user  may
              list  the  cloud  metadata,  provided they are in the group that
              they are listing the cloud metadata for.
 
       **metadata-load**  
              Add a local file as cloud metadata to a  cloud  in  the  current
              group.   Any  user may add cloud metadata to a cloud definition,
              provided they are in the group that the cloud  they  are  adding
              metadata to is in.
 
       **metadata-update**  
              Update  information  about  a cloud metadata file in the current
              group.  Any user may update cloud metadata, provided they are in
              the group that the cloud metadata is in.
 
       **status** 
       Lists  the  status  of  Virtual Machines (VMs) and jobs for each 
              cloud within the current group.  Any user  may  view  the  cloud
              status, provided they are in the group that they are viewing the
              cloud status for.
 
       **update** 
       Modifies the cloud definitions within the  current  group.   Any 
              user  may  update  a  cloud definition, provided they are in the
              group that they are modifing the cloud definition for.
 
**SEE ALSO**  
       **csv2** 
       (1) **csv2_cloud_add** 
       (1) **csv2_cloud_delete** 
       (1) **csv2_cloud_list** 
       (1) 
       **csv2_cloud_metadata-collation** 
       (1) **csv2_cloud_metadata-delete** 
       (1) 
       **csv2_cloud_metadata-edit** 
       (1) **csv2_cloud_metadata-list** 
       (1) 
       **csv2_cloud_metadata-load** 
       (1) **csv2_cloud_metadata-update** 
       (1) 
       **csv2_cloud_status** 
       (1) **csv2_cloud_update** 
       (1) 
 
 
 
cloudscheduler version 2        7 November 2018              cloudscheduler(1)
 
