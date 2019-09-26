# Cloud Scheduler version 2

A csv2_htc_agent is required for each HTCondor instance using CSV2's VM provisioning. 
Every instance of CSV2 has HTCondor and this agent installed and running. If you wish 
CSV2 to provision VMs for your stand-alone (remote) HTCondor job scheduler, you will
need to install csv2_htc_agent on that machine. 

To install csv2_htc_agent, issue the following command on your remote HTCondor host::

    curl https://<fqdn_of_the_csv2_host>/repo/install_remote_csv2_htc_agent.sh | bash

The script will explain what is required and what it does. If the requirements are met,
the csv2_htc_agent service will be installed and started..  
