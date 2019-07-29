Architecture
============

.. image:: ArchitectureFunctional.svg


.. The Use Interface (UI) consisting of web browsers, the command line interface (cloudscheduler command), and
   the RESTful Apache web service.
.. Data services consisting of a relational database (MariaDB), RPC/Signalling (RabbitMQ server/csv2_htc_agent clients),
   together with InfluxDB/Plotly for timeserires reporting.
.. Data gatherers to retrieve data from Condor, Openstack, EC2, and other sources.
.. Job management is via the HTCondor job scheduler.
.. Cloud management currently supports Opentack and Amazon EC2 clouds.

.. toctree::
   :maxdepth: 2
   :caption: CSV2 is composed of the following functional areas:

   _data_services/index
   _data_gathering/index
   _job_scheduling/index
   _vm_scheduling/index
   _user_interfaces/index
   _utilities/index

