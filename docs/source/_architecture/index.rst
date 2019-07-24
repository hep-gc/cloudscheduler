Architecture
============

.. image:: ArchitectureFunctional.svg

CSV2 is composed of the following functional areas:

#. The Use Interface (UI) consisting of web browsers, the command line interface (cloudscheduler command), and
   the RESTful Apache web service.
#. Data services consisting of a relational database (MariaDB), RPC/Signalling (RabbitMQ server/csv2_htc_agent clients),
   together with InfluxDB/Plotly for timeserires reporting.
#. Data gatherers to retrieve data from Condor, Openstack, EC2, and other sources.
#. Job management is via the HTCondor job scheduler.
#. Cloud management currently supports Opentack and Amazon EC2 clouds.
