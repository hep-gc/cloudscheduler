Utility: csview
===============

csview reads the directory *.../cloudscheduler/schema/views*' and updates the database
by recreating all defined views. It is normally invoked during the upgrade process by the
**db_upgrade** utility but can be run as a stand-alone utility.

Since views can be dependent on one another, the order of recreation is critical. csview 
analyses dependencies and recreates the views in the appropriate order.

Additionally, csview can be used to map defined views to show it's dependencies. 

Synopsis: csview [ map <view_name | ALL> | redefine ]

