All tarballs in this directory are created using a relative path but are intended to be 
installed in the "/opt" directory. The procedure is as follows:

    - cd /tmp
    - wget https://<csv2_fqdn/repo/<tarball_name>
    - cd /opt
    - tar -xzvf /tmp/<tarball_name>

When these steps have been completed, the utility */opt/cloudsheduler/utilities/remote_condor_poller_enable* should
be run as root to complete the installation.
