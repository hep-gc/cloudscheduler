Data Gathering
==============


 System data regarding the state of cloudscheduler and the interfaced systems is gathered via a fleet of pollers implemented in python. This data is stored in a MariaDB database for use by all of the cloudscheduler services.
 Each poller is responsible for a different subset of data which is outlined in more detail on the pages linked below.

.. toctree::
   :maxdepth: 2
   :caption: CSV2 seperates data polling into the following categories:

   _condor/index
   _openstack/index
   _ec2/index
   _other/index
