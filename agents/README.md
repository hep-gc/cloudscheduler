# Cloud Scheduler version 2 Agents

A csv2_htc_agent is required for each HTCondor instance using CSV2's VM provisioning. 
Every instance of CSV2 has HTCondor and this agent installed and running. If you wish 
CSV2 to provision VMs for your stand-alone (remote) HTCondor job scheduler, you will
need to install csv2_htc_agent on that machine. 

You can review the installation command with the following:

    curl https://<fqdn_of_the_csv2_host>/repo/install_remote_csv2_htc_agent.sh | less
    
or install csv2_htc_agent by piping the script to bash:

    curl https://<fqdn_of_the_csv2_host>/repo/install_remote_csv2_htc_agent.sh | bash

The script will explain what is required and what it does. If the requirements are met,
the csv2_htc_agent service will be installed and started..  
