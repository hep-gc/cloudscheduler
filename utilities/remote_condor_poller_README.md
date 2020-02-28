To complete the installation of a remote condor_poller, run:

    sudo /opt/cloudscheduler/utilities/remote_condor_poller_enable

This bash script will:

1. Verify all prerequisite software has been installed, installing and updating
   as necessary:
    - Python3/Pip3
    - boto3
    - htcondor
    - python-keystoneclient
    - python-novaclient
    - SQLAlchemy

2. Copy the systemd unit file for the condor poller to the systemd directory.

3. Enable and start the condor_poller.

