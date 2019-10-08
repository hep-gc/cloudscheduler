Openstack Poller
==============

The openstack poller is a multi-proccess python program that leverages the openstack python libraries to gather important data from openstack clouds registered with csv2.

There is individual processes for gathering data about the VMs, Machine Images, Flavours, Networks, Quotas, and Keypairs that are available to the registered openstack project(tenant). Each of these processes uses the relevent openstack api (nova, glance, etc) to get the most up to date information and stores it in csv2's mariaDB database. Csv2's main scheduler uses the quota and flavour information to calculate how many VMs it's able to boot on the cloud.

The openstack poller also contains a registrar process that registers the poller's status with csv2 such that end users can be notified if there is a failure in the poller and user action is required.

