# Cloud Scheduler version 2

A re-design and re-write of Cloud Scheduler in Python 3. Documentation for the new system may be found at
[readthedocs](https://cloudscheduler.readthedocs.io).

For installation, please follow the instructions ![here](ansible-playbook/README.md).

## Road Map:
- Previous stable-2.5 - Auto GSI and firewall configuration.
- Previous stable-2.6 - Glint integration, HTCondor GSI polling and accounting.
- Previous stable-2.7 - AMQP authentication and multi-host signalling.
- Previous stable-2.8 - SQLalchemy Removal
- Previous stable-2.9 - Openstack application Credential Support and Openstack volume management.
- Previous stable-2.9.1 - Bugfixes & slot accounting
- Previous stable-2.9.2 - Web forum and QoL upgrades
- Previous stable-2.10.1 - Backend webserver upgrades and additional group/cloud controls
- Previous: stable-2.10.2 - Process watchdog & web interface bugfixes
- Previous: stable-2.10.3b - Public status page, openstack volume type support, & condor poller installation script
- Previous: stable-2.10.4 - Poller and database performance optimizations & image cache cleanup
- Previous: stable-2.10.5 - Image compression options, public status page plotting, & ssl influxdb implementation 
- Current: stable-2.10.6:
   - Repo cleanup: removed unused files and development machine specific schema backups
   - Updates to deafult configuration and schema for use outside heprc
   - forward http requests to the https site area

   
# Future Plans:
