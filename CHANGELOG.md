# Cloud Scheduler version 2 Change Log


- stable-2.7.1:
  - Features
    - CLI Support & manpages for Image management
      - List
      - Delete
      - Transfer
      - Upload
    - Defaults replication modified to only transfer to/from clouds that have an active network and are enabled.
    - Update default yaml to automatically insert condor worker certs onto the vm from the values obtained by the condor pollers
    - Added new optional parameter "volume_type" to boot volume yaml
    - Add boot volume field for openstack clouds and update field validation.
    - Upgrade openstack cloud error reporting when trying to boot VMs with volumes.
    - Update field validation regular expressions to allow comma seperated values.
    - Update the default logrotate files.
  - Bugfixes
    - Capture and manage decode error in csmain when retrieving yaml files from the database
    - Fix bug in vm termination that would cause all operations to be skipped after a single failure
    - Condense logging in several pollers.
    - Fix bug in ec2_filterer that caused a crash when receiving cloud update signlas.
    - Fix bug in condor poller that caused job and machine entries to be purged from the database on a failed polling cycle.
    - Fix bug in keypair transfer that would cause the system to chose a source keypair from an offline cloud causing the process to fail.
    - Fix bug in image and key webui that would cause the redirect after a submission to change the users active group.

- stable-2.7.0:
  - Introduction of this change log.

  - AMQP used for signalling:
    - Introduction of csv2-signal-agent service.

  - All AMQP requests to be authenticated with user name and password. The guest account is locked.


  - TLS termination through HAProxy for all remote AMQP requests.

  - Process monitor changes:
    - graceful shutdown of services.
    - pause services for backup. 
    - self reporting service statuses.
    - Manage dynamic subprocess identified by SQL select.

  - Removal of 'target_clouds'.
  
  - Removal of apel_accounting

  - db_upgrade utility enhancements:
    - When in batch mode ('-i' option), error message and exit (rather than prompt) when manual input required.
    - Ephemeral data conversion: passes temporary directory to schema_backup and loads/converts the ephemeral
      data from there.

  - schema_backup utility enhancement:
    - New option (specifies temporary directory) to save ephemeral data.
    - To use service pause and release when taking backups.

  - Cloud control via dedicated subprocesses for each cloud:
    - The scheduler (csmain) starts one subprocess for each group/cloud to manage VM termination.
    - The condor poller starts one subprocess for each group/cloud to manage condor machine retirement.  

 
  - OpenStack credentials now verified prior to adding or updating any cloud.
  
  - Certificate Management Improvements
  
  - Configuration table merge and cleanup 
  
  - Seperate logrotate files
  
  - Ansible installation playbook re-organization/enhancements.
  
  - Fixes:
    - Server configuration request to ignore the 'group' key (passed on all requests).
    - Log level change without service restart.
    - Ignore invalid default_group user setting (picks first valid group). 
    - Remove group related data from tables (aliases, default groups, etc) when a group is deleted.
    - Cleanup local inventories to remove obsolete items at the end of each polling cycle.

