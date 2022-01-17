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
- Previous stable-2.9.1 Focus: Bugfixes & slot accounting
   - New process to double check vm slot accounting
   - #243 Audit/fix VM overlay
   - #301 Disabled clouds should have their numbers greyed out as to provide clarity for why they are missing from totals
   - #304 Make boot volume text field bigger on clouds page so it is more readable 
   - #318 Fix web part or server side code so that you can actually remove the last security group on clouds page
   - #319 Fix Iframe recursion in metadata editor, view needs to return the editor on failed post
   - #325 Fix/update nav bar on image//keys page; update top margin to be dynamically set by the thickness of nav bar (ie narrow screen)
   - #328 Slot counts displayed incorrectly 
   - #epic ticket #?? Add signal to kill retire command to kick pollers;
   - #321 Audit message & error message strings so they are displayed in the correct format
   - #327 Stop user from deleting cloud if VMs still exist
   - #201 Cut down default yaml
- Previous stable-2.9.2 Focus: New Development
   - #294//322 Metadata display: Colour code for enable/disable, list in priority order, add checksum for add/update and put it on display
   - #292 Add None value override for all cloud level options so you can disable the default for a particular cloud
   - #epic ticket: Save plots from webui; During image upload add detection for format
   - #314 Retain form data on failed submission
   - #323 Add place to submit report//bug; add link to /repo/ for condor poller install, make version a link to the github tag
   - #?? update default work cert location in template file; change poller to ignore the rest of the process when finding condor cert if the condor variable is not set
- Next stable-2.10.1
   Fix:
   - #371 Debug openstack vm poller sleep problem 
   - #368 Fix job table dropdown content for target alias
   - #346 Fix view total used resources table to handle cloud unreachable case
   - #366 Disable removal of group when there are vms in it
   - #370 Clean up condor gsi configs when not use gsi anymore
   Feature:
   - #356 Add description for cloud config fields
   - #367 Enable removal of cloud alias
   - #369 Enable a cloud pause feature
   - check on entries in the slow query log
   - Halt external connections on the database while upgrade underway
   - enable public status page
   - change installer routine to remove files from previous releases that are no longer needed
   - list of all supported csv2 variables and JDL options to boot a VM
   
# Future Plans:
## Double checking
- #329 Audit log rotate for all log files 
- #311 Check boot algorithm to see we still do not boot per group (ie shared clouds are throttled)
- #312 Check if target image still works when specified in job
- #315 Check view groups_of_idle_jobs to seeif flavors are listed in priority order (done in v2.10.0)

## Other development
- #201 Cut down default yaml
- #?  Invalidate class ads on kill command
- #?? update default work cert location in template file; change poller to ignore the rest of the process when finding condor cert if the condor variable is not set
