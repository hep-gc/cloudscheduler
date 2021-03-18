# Cloud Scheduler version 2

A re-design and re-write of Cloud Scheduler in Python 3. Documentation for the new system may be found at
[readthedocs](https://cloudscheduler.readthedocs.io).

For installation, please follow the instructions ![here](ansible-playbook/README.md).

## Road Map:
- Previous stable-2.5 - Auto GSI and firewall configuration.
- Previous stable-2.6 - Glint integration, HTCondor GSI polling and accounting.
- Previous stable-2.7 - AMQP authentication and multi-host signalling.
- Current stable-2.8 - SQLalchemy Removal
- stable-2.9 - Openstack application Credential Support and Openstack volume management.
  - Refactor Openstack code to one library (currently split at least 4 places: csmain, openstack poller, glint, web-frontend)
    - looking at replacing openstack-clients with the all-encompassing openstacksdk
  - Update web-frontend to accept and validate application credentials
  - Update openstack poller to poll Volumes
  - Update scheduler algorithm to account for volume limits
