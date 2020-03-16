All tarballs in this directory are created using a relative path but are intended to be 
installed in the "/opt" directory. The procedure is as follows:

    - cd /tmp
    - wget https://<csv2_fqdn/repo/<tarball_name>
    - tar -xzvf /tmp/<tarball_name>
    - rsync -av cloudscheduler /opt/cloudscheduler

When these steps have been completed, the file **/opt/cloudsheduler/utilities/README.md** contain instructions on how 
to complete the installation of the function downloaded.
