The files in this directory represent the pieces required to have two services running on a condor
machine that will collect job and machine data and package them up and send them to a central redis server.

First clone the repo into /opt/

The files must be set up on the system as follows:
```
/opt/cloudscheduler/data_collectors/cspollers.logrotate                -> /etc/logrotate.d/cspollers.logrotate
/opt/cloudscheduler/data_collectors/condor/cscollector.service         -> /etc/systemd/system/cscollector.service
/opt/cloudscheduler/data_collectors/condor/csjobs.service              -> /etc/systemd/system/csjobs.service
/opt/cloudscheduler/data_collectors/openstack/csmetadata.service       -> /etc/systemd/system/csmetadata.service
/opt/cloudscheduler/data_collectors/condor/condor_data_collectors.yaml -> /etc/condor_data_collectors.yaml
 (the config.py will look to the /opt/cloudscheduler/data_collectors/condor location if not found here)
/opt/cloudscheduler/data_collectors/openstack/openstack_poller.yaml    -> /etc/openstack_poller.yaml
 (the config.py will look to the /opt/cloudscheduler/data_collectors/openstack location if not found here)
```

A new user will also be used:
sudo adduser cloudscheduler -s /sbin/nologin

This user must have permissions with htcondor otherwise the services will be unable to run commands

lastly we need to create the log files that these services write to and change the owner to the relevent user we created
```
mkdir /var/log/cloudscheduler
touch /var/log/cloudscheduler/csjobs.log
touch /var/log/cloudscheduler/cscollector.log
touch /var/log/cloudscheduler/openstackpoller.log
chown cloudscheduler:cloudscheduler /var/log/cloudscheduler
chown cloudscheduler:cloudscheduler /var/log/cloudscheduler/csjobs.log
chown cloudscheduler:cloudscheduler /var/log/cloudscheduler/cscollector.log
chown cloudscheduler:cloudscheduler /var/log/cloudscheduler/openstackpoller.log
```

Once the files are in place and the users are created reload the daemons and start the services:
```
sudo systemctl daemon-reload
sudo systemctl start csjobs
sudo systemctl start cscollector
sudo systemctl start csmetadata
```
