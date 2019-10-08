Machine Poller
==============

The cloudscheduler machine poller in a multi-proccess python program that has 3 tasks. Firstly it uses the htcondor python bindings to query all condor instances registered as csv2 groups for a complete list of machine classads. These machine classads are sorted into the various group and cloud combinations and inserted into csv2's mariaDB database. These machine classads are then monitored by csv2's main scheduler to make decisions about increasing or reducing the number of running VMs to match the job queue. This data is also used to track the state of VMs and how many slots on a given machine are running.

The second process is known as the command poller which performs condor and cloud commands via the relevent python APIs. These commands are issued by the cloudscheduler system setting flags in the database. Based on these flads the command poller issues commands such as retiring a machine, cleaning up classads and eventually terminating VMs.

Lastly there is a registrar process that reports on the status of this poller so the end user can be made aware if the poller goes offline for any reason.

