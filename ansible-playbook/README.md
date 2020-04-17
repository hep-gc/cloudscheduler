The Ansible playbook contained within this directory will build cloudscheduler version 2
in a machine with the fully qualified domain name (FQDN) of "csv2-sa.heprc.uvic.ca". To
reset the FQDN, run:

    ../utilities/reset_stand_alone_hostname
    
The target machine should have the following characteristics:

   - Real or virtual.
   - At least 2 cores
   - At least 4 GiB of memory.
   - A root block device with CentOS 7 installed; at least 50 GiB is recommeded.
   - A storage block device; At least 50GiB is recommended.
   - Root login from the deployment host via ssh key.

Once CentOS has been installed, modify the "secrets" and the "vars" within
this directory to contain appropriate values. Comments within the files should explain what
is required. The playbook can then be applied with the following command:

    ansible-playbook -e addenda=addenda -i inventory csv2-sa.yaml -u root

When the installation completes, point your browser at "https://your_fqdn" and login with
"csv2_default" user and the password you set in "secrets".

Alternatively, you can also use this playbook to build a cloudscheduler version 2 container build to function
alongside three other containers with MariaDB, HTCondor, and InfluxDB.

Ansible Bender is required to use this playbook to build the container image.

Once it is installed modify the "secrets" and "vars" within this directory to contain appropriate values
making sure the "container" variable in the "vars" file is set to `True`. The container image can then 
be build with the following command:

    ansible-bender build csv2-cont.yaml

Make sure you recreate the symlinks in the roles/csv2/vars directory if you are copying to another machine to run ansible-bender
