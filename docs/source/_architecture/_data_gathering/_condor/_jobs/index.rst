Job Poller
==============

The cloudscheduler job poller in a multi-proccess python program that has 3 responsibilities. Firstly it uses the condor python bindings to query all condor instances registered as csv2 groups for their job classads. These jobs are sorted into the various groups (or ignored as foreign if they are not valid csv2 jobs) and inserted into csv2's mariaDB database. These job classads are then used by csv2's main scheduler to make decisions about booting new VMs to execute the jobs.
The second process is known as the command poller which supports functions such as holding jobs. Currently this portion of the poller is not in use by the csv2 system.
Lastly there is a registrar process that reports on the status of this poller so the end user can be made aware if the poller goes offline for any reason.

