Utility: reset_stand_alone_hostname
===================================

As distributed, the stand-alone Ansible playbook contained within *.../cloudscheduler/ansible-playbook*
will install CSV2 in a target host with the fully qualified domain name (FQDN) of **csv2-sa.heprc.uvic.ca**.
This domain is useable by the CSV2 developers only.
The utility **reset_stand_alone_hostname** is provided to allow other users of CSV2 to reset the playbook
to a target FQDN of their choice.
The utility and playbook may be used repeatedly to create multiple installations.

Synopsis: reset_stand_alone_hostname <target_FQDN>

Note: if the "<target_FQDN>" is omitted, the utility will prompt for it.

