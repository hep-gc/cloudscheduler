![csv2](/images/csv2_logo.png)

A re-design and re-write of Cloud Scheduler in Python 3. Documentation for the new system may be found at
[readthedocs](https://cloudscheduler.readthedocs.io).

For installation, please follow the instructions for our ansible-playbook ![here](https://github.com/hep-gc/uvic-heprc-ansible-playbooks/blob/master/roles/csv2/README.md).

## Road Map:
- stable-2.5 - Auto GSI and firewall configuration.
- stable-2.6 - Glint integration, HTCondor GSI polling and accounting.
- stable-2.7 - AMQP authentication and multi-host signalling.
- [stable-2.8](https://github.com/hep-gc/cloudscheduler/releases/tag/stable-2.8.0) - SQLalchemy Removal
- stable-2.9 - Openstack application Credential Support and Openstack volume management.
- stable-2.9.1 - Bugfixes & slot accounting
- stable-2.9.2 - Web forum and QoL upgrades
- stable-2.10.1 - Backend webserver upgrades and additional group/cloud controls
- stable-2.10.2 - Process watchdog & web interface bugfixes
- stable-2.10.3b - Public status page, openstack volume type support, & condor poller installation script
- stable-2.10.4 - Poller and database performance optimizations & image cache cleanup
- stable-2.10.5 - Image compression options, public status page plotting, & ssl influxdb implementation 
- Current: stable-2.10.6:
   - Repo cleanup: removed unused files and development machine specific schema backups
   - Updates to deafult configuration and schema for use outside heprc
   - forward http requests to the https site area

   
# Future Plans:
- stable-2.11.0
  - return of limited ec2 support
  - #378 show all alias' on status page
  - #379 Remove trailing form whitespace
  - #382 Stop accidental update POST requests
  - #384 Improve warnings for application & certificate expiary
  - #390 Fix plotting issues when more than one VM trace are active
