# Cloud Scheduler version 2/HTCondor Agent

A csv2_htc_agent is required for each HTCondor instance using CSV2's VM provisioning. 
Every instance of CSV2 has HTCondor and this agent installed and running. If you wish 
CSV2 to provision VMs for your stand-alone (remote) HTCondor job scheduler, you will
need to install csv2_htc_agent on that machine. 

You can download the installation script with the following command:

    curl -o install_remote_csv2_htc_agent.sh https://<fqdn_of_the_csv2_host>/repo/install_remote_csv2_htc_agent.sh 
    
to check what it is doing. To install the HTCondor Agent, do the following:

    chmod +x install_remote_csv2_htc_agent.sh 
    ./install_remote_csv2_htc_agent.sh 

The script will explain what is required and what it does. If the requirements are met,
the csv2_htc_agent service will be installed and started..  
