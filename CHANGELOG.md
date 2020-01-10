# Cloud Scheduler version 2 Change Log

- stable-2.7.0:
  - Introduction of this change log.

  - AMQP used for signalling:
    - Introduction of csv2-signal-agent service.

  - Process monitor changes:
    - graceful shutdown of services.
    - pause services for backup.

  - Removal of 'target_clouds'.

  - db_upgrade utility enhancements:
    - When in batch mode ('-i' option), error message and exit (rather than prompt) when manual input required.
    - Ephemeral data conversion: passes temporary directory to schema_backup and loads/converts the ephemeral
      data from there.

  - schema_backup utility enhancement:
    - New option (specifies temporary directory) to save ephemeral data.
    - To use service pause and release when taking backups.

  - Fixes:
    - Server configuration request to ignore the 'group' key (passed on all requests).
     
