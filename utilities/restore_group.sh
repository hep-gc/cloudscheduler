#!/bin/bash
###
### This utility must be run as root. It performs the following:
###
### 1.  Adds a 'default' group to csv2_groups table
### 2.  Inserts 'default' group to csv2_user_groups along with any superusers from the csv2_user table

mysql csv2 -e "
insert ignore into csv2_groups (group_name) values ('default');
insert into csv2_user_groups (username, group_name)
select username, 'default'
from csv2_user
where is_superuser = 1
on duplicate key update group_name='default';
"
