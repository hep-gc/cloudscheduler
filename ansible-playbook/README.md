The Ansible playbook contained within this directory will build cloudscheduler version 2
in a machine with the fully qualified domain name (FQDN) specified in the "inventory" file. 
    
The target machine should have the following characteristics:

   - Real or virtual.
   - At least 2 cores
   - At least 4 GiB of memory.
   - A root block device with CentOS 7 installed; at least 50 GiB is recommeded.
   - A storage block device; At least 50GiB is recommended.
   - Root login from the deployment host via ssh key.

Once CentOS has been installed, add the machine you want to install csv2 to in the "inventory" file 
and modify the "secrets" and the "vars" within this directory to contain appropriate values. 
Comments within the files should explain what is required. 
The playbook can then be applied with the following command:

    ansible-playbook -i inventory csv2.yaml -u root

When the installation completes, point your browser at "https://your_fqdn" and login with
"csv2_default" user and the password you set in "secrets".

