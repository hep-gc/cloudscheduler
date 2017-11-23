The files in this directory represent the pieces required to have two services running on a condor
machine that will collect job and machine data and package them up and send them to a central redis server.

First clone the repo into /opt/

The files must be set up on the system as follows:

/etc/systemd/system/cscollector.service
/etc/systemd/system/csjobs.service
/etc/condor_data_collectors.cfg (the config.py will look to the /opt/cloudscheduler/data_collectors/condor location if not found here)

Two new users will also be used:
sudo adduser csjobs -s /sbin/nologin
sudo adduser cscollector -s /sbin/nologin

These users must have permissions with htcondor otherwise the services will be unable to run commands

lastly we need to create the log files that these services write to and change the owner to the relevent user we created
note that we can definitly use the same user here if we like, but they must have permissions with condor to execute the python binding commands
touch /var/log/csjobs.log
touch /var/log/cscollector.log
chown csjobs:csjobs /var/log/csjobs.log
chown cscollector:cscollector /var/log/cscollector.log

Once the files are in place and the users are created reload the daemons and start the services:
sudo systemctl daemon-reload
sudo systemctl start csjobs
sudo systemctl start cscollector
