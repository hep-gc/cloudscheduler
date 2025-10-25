#!/bin/bash

mysql csv2 -e "
insert into csv2_groups (group_name) values ('default');
insert into csv2_user_groups (username, group_name)
select username, 'default'
from csv2_user
where is_superuser = 1
on duplicate key update group_name='default';
"
