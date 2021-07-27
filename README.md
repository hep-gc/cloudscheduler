# Cloud Scheduler version 2

A re-design and re-write of Cloud Scheduler in Python 3. Documentation for the new system may be found at
[readthedocs](https://cloudscheduler.readthedocs.io).

For installation, please follow the instructions ![here](ansible-playbook/README.md).

## Road Map:
- Previous stable-2.5 - Auto GSI and firewall configuration.
- Previous stable-2.6 - Glint integration, HTCondor GSI polling and accounting.
- Previous stable-2.7 - AMQP authentication and multi-host signalling.
- Previous stable-2.8 - SQLalchemy Removal
- Current stable-2.9 - Openstack application Credential Support and Openstack volume management.
- stable-2.9.1 Focus: Bugfixes & slot accounting
   - New process to double check vm slot accounting
   - #243 Audit/fix VM overlay
   - #301 Disabled clouds should have their numbers greyed out as to provide clarity for why they are missing from totals
   - #? Make boot volume text field bigger on clouds page so it is more readable  ----- increase the width to 200
   - #318 Fix web part or server side code so that you can actually remove the last security group on clouds page
   - #319 Fix Iframe recursion in metadata editor, view needs to return the editor on failed post ----- start
   - #325 Fix/update nav bar on image//keys page; update top margin to be dynamically set by the thickness of nav bar (ie narrow screen) ----- done
   - #328 Slot counts displayed incorrectly
   - #epic ticket #?? Add signal to kill retire command to kick pollers;
   - #321 Audit message & error message strings so they are displayed in the correct format ----- done
   - #327 Stop user from deleting cloud if VMs still exist ----- done
   - #201 Cut down default yaml
- stable-2.9.2 Focus: New Development
   - #294//322 Metadata display: Colour code for enable/disable, list in priority order, add checksum for add/update and put it on display
   - #292 Add None value override for all cloud level options so you can disable the default for a particular cloud
   - #epic ticket: Save plots from webui; During image upload add detection for format
   - #314 Retain form data on failed submission
   - #323 Add place to submit report//bug; add link to /repo/ for condor poller install, make version a link to the github tag
   - #?? update default work cert location in template file; change poller to ignore the rest of the process when finding condor cert if the condor variable is not set

# Future Plans:
## Web Interface Work
### Fixes
- #243 Audit/fix VM overlay
- #301 Disabled clouds should have their numbers greyed out as to provide clarity for why they are missing from totals
- #? Make boot volume text field bigger on clouds page so it is more readable
- #318 Fix web part or server side code so that you can actually remove the last security group on clouds page
- #319 Fix Iframe recursion in metadata editor, view needs to return the editor on failed post
- #325 Fix/update nav bar on image//keys page; update top margin to be dynamically set by the thickness of nav bar (ie narrow screen) ---- done
- #328 Slot counts displayed incorrectly

### New development
- #294//322 Metadata display: Colour code for enable/disable, list in priority order, add checksum for add/update and put it on display
- #292 Add None value override for all cloud level options so you can disable the default for a particular cloud
- #epic ticket: Save plots from webui; During image upload add detection for format
- #314 Retain form data on failed submission
- #323 Add place to submit report//bug; add link to /repo/ for condor poller install, make version a link to the github tag


## Serverside web work
- #epic ticket #?? Add signal to kill retire command to kick pollers;
- #321 Audit message & error message strings so they are displayed in the correct format ----- done
- #327 Stop user from deleting cloud if VMs still exist

## Double checking
- #329 Audit log rotate for all log files ----- in progress, under testing
- #311 Check boot algorithm to see we still do not boot per group (ie shared clouds are throttled)
- #312 Check if target image still works when specified in job
- #315 Check view groups_of_idle_jobs to seeif flavors are listed in priority order

## Other development
- #201 Cut down default yaml
- #?  Invalidate class ads on kill command
- #?? update default work cert location in template file; change poller to ignore the rest of the process when finding condor cert if the condor variable is not set
