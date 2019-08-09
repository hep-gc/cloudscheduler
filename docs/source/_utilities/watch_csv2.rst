Utility: watch_csv2
===================

The **watch_csv2** is provided to monitor the CSV2 scheduling process, much like the web/CLI **status**
display. Unlike the status display, **watch_csv2**  must be run on the CSV2 server and excutes configurable
commands and SQL statements periodically to produce a fine-grained monitoring status. The utility is run
as a service to produce a log file of database snapshots taken once every ten seconds (also configurable)
and saved within */var/log/cloudschedler/watch_csv2.log*.

The utility can also be run interactively for one of the following purposes:

* To monitor the real-time status.
* To replay the log files created by the **watch_csv2** service.
* To rotate watch_csv2 log files.
* To map watch_csv2 log files.

When monitoring real-time status or replaying log files, **watch_csv2** uses **curses** to create a
fullscreen, interractive display rather like the **top** command. Functions are provide to move 
backward and foward within log files and to search for specific events.

Synopsis:

To monitor the real-time status::

    watch_csv2

To replay the log files created by the **watch_csv2** service::

    watch_csv2 --replay

For all other options, use the command::

    watch_csv2 --help

Configuration
^^^^^^^^^^^^^

**watch_csv2** has two types of configuration:

#. Configuration items within the database:

   * **category=watch_csv2, key=config_file** - specifies the file containing the commands and SQL statements to be excuted (see below). These commands will be issued perioducally in a loop and the results displayed either interractively or saved within a log file. By default, this file is *.../cloudscheduler/etc/watch_csv2.conf*.

..

   * **category=watch_csv2, key=log_file** - specifies the log file where the **watch_csv2** service is to to save monitoring data. By default, this file is */var/log/cloudscheduler/watch_csv2.logging*.  

..

   * **category=watch_csv2, key=sleep_time** - specififies, in seconds, the sleep time between loop iterations. The default is 10 seconds.

#. Command and SQL statement configuration within the **watch_csv2** configuration file must adhere to the following rules:

   * All commands and SQL statements must end with a semi-colon (";").
   * All commands must be valid system commands.
   * All SQL statements bust be valid select statements for the CSV2 database and CSV2 user.

   A standard configuration file, *.../cloudscheduler/etc/watch_csv2.conf*, is provided with the distribution. Please refer to that file and
   the database schema documentation for more information.

