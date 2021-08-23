from django.core.exceptions import PermissionDenied

import time
import boto3
from datetime import datetime

from cloudscheduler.lib.schema import *
from cloudscheduler.lib.openstack_functions import get_openstack_sess, get_openstack_api_version, get_keystone_connection, get_nova_connection
from cloudscheduler.lib.log_tools import get_frame_info

import keystoneclient.v2_0.client as v2c
import keystoneclient.v3.client as v3c

'''
UTILITY FUNCTIONS
'''

#-------------------------------------------------------------------------------

def cskv(key_values, opt='dict'):
    """
    Parse comma separated key/value pairs. Values containing commas and null
    values must be quoted.
    """

    msg = None
    rc = 0  

    if opt == 'dict':
        result = {}
    else:
        result = []

    if key_values:
        while len(key_values) > 0:
            key_value = key_values.split('=', 1)
            if len(key_value) == 2:
                if len(key_value[1]) > 0 and key_value[1][0] == "'": 
                    value_key_values = key_value[1][1:].split("'", 1)
                elif len(key_value[1]) > 0 and key_value[1][0] == '"': 
                    value_key_values = key_value[1][1:].split('"', 1)
                else:
                    value_key_values = key_value[1].split(',', 1)

                if len(value_key_values) == 2:
                    if opt == 'dict':
                        result[key_value[0]] = value_key_values[0]
                    else:
                        result.append([key_value[0], value_key_values[0]])

                    if len(value_key_values[1]) > 0 and value_key_values[1][0] == ',': 
                        key_values = value_key_values[1][1:]
                    else:
                        key_values = value_key_values[1]

                else:
                    if len(key_value[1]) > 0 and (key_value[1][0] == "'" or key_value[1][0] == '"'):
                        msg = 'end quote missing from value ((key "%s").' % key_values
                        rc = 1
                        break
                    else:
                        if len(value_key_values[0]) > 0:
                            if opt == 'dict':
                                result[key_value[0]] = value_key_values[0]
                            else:
                                result.append([key_value[0], value_key_values[0]])
                            key_values = ''
                        else:
                            msg = 'null values must be quoted ((key "%s").' % key_values
                            rc = 1
                            break

            else:
                msg = 'no value specified ((key "%s").' % key_values
                rc = 1
                break

    return rc, msg, result

#-------------------------------------------------------------------------------

def diff_lists(list1,list2, option=None):
    """
    if option equal 'and', return a list of items which are in both list1
    and list2. Otherwise, return a list of items in list1 but not in list2.
    """

    if option and option == 'and':
        return [x for x in list1 if x in list2] 
    else:
        return [x for x in list1 if x not in list2] 

#-------------------------------------------------------------------------------

def kill_retire(config, group_name, cloud_name, option, count, updater_str):

#   print(">>>>>>>>>>>>>>>>>>>>>", group_name, cloud_name, option, count, updater_str)

    # Process "control [cores, ram]".
    if option == 'control':
        def count_int(val):
            try:
                return int(val)
            except:
                return -1

        if count_int(count[0]) > -1:
            core_max = count[0]
        else:
            core_max = 999999999999

        if count_int(count[1]) > -1:
            ram_max = count[1]
        else:
            ram_max = 999999999999

        s = 'set @cores=0;'
        rc, msg = config.db_execute(s)
        s = 'set @ram=0;'
        rc, msg = config.db_execute(s)
        s = 'create or replace temporary table kill_retire_priority_list as select * from (select *,(@cores:=@cores+flavor_cores) as cores,(@ram:=@ram+flavor_ram) as ram from view_vm_kill_retire_priority_idle where group_name="%s" and cloud_name="%s" and killed<1 and retired<1 order by priority asc) as kpl where cores>%s or ram>%s' % (group_name, cloud_name, core_max, ram_max) 
        #print("setting up kill retire priority list")
        rc, msg = config.db_execute(s)
        if rc != 0:
            print("Error setting up temp table kill_retire_priority_list:")
            print(msg)
            print("Unable to retire VMs..")
            config.db_rollback()
            return 0
        #print("updating csv2_vms to retire")
        rc, msg = config.db_execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set retire=1, updater="%s:r1" where kpl.vmid is not null' % updater_str)
        if rc != 0:
            print("Error updating VMs from kill_retire_priority_list:")
            print(msg)
            print("Unable to retire VMs..")
            config.db_rollback()
            return 0
        else:
            print("update executed..")
    
    # Process "kill N".
    elif option == 'kill':
        if updater_str is None:
           print("Updater string empty, assigning default value.")
           updater_str = "kill_retire"
        if cloud_name == '-':
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_idle where group_name="%s" and killed<1 order by priority desc limit %s' % (group_name, count)
        else:
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_idle where group_name="%s" and cloud_name="%s" and killed<1 order by priority desc limit %s' % (group_name, cloud_name, count)

        config.db_execute(s)
        config.db_execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set terminate=2, updater="%s:t2" where kpl.vmid is not null' % updater_str)

    # Process "retire N".
    elif option == 'retire':
        if updater_str is None:
           print("Updater string empty, assigning default value.")
           updater_str = "kill_retire"
        if cloud_name == '-':
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_age where group_name="%s" and machine is not null and killed<1 and retired<1 order by priority desc limit %s' % (group_name, count)
        else:
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_age where group_name="%s" and cloud_name="%s" and machine is not null and killed<1 and retired<1 order by priority desc limit %s' % (group_name, cloud_name, count)

        config.db_execute(s)
        config.db_execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set retire=1, updater="%s:r1" where kpl.vmid is not null' % updater_str)

    # Process "retain N".
    elif option == 'retain':
        if updater_str is None:
           print("Updater string empty, assigning default value.")
           updater_str = "kill_retire"
        if cloud_name == '-':
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_age where group_name="%s" and killed<1 and retired<1 order by priority asc limit %s, 999999999999' % (group_name, count)
        else:
            s = 'create or replace temporary table kill_retire_priority_list as select * from view_vm_kill_retire_priority_age where group_name="%s" and cloud_name="%s" and killed<1 and retired<1 order by priority asc limit %s, 999999999999' % (group_name, cloud_name, count)

        config.db_execute(s)
        config.db_execute('update csv2_vms as cv left outer join (select * from kill_retire_priority_list) as kpl on cv.vmid=kpl.vmid set retire=1, updater="%s:r=1" where kpl.vmid is not null' % updater_str)
    
    
    rc, msg = config.db_execute('select count(*) as count from kill_retire_priority_list')
    retired_list = []
    for row in config.db_cursor:
        print("Kill retire row: %s" % row)
        retired_list.append(row)

    if len(retired_list) > 0:
        return retired_list[0]['count']
    else:
        return 0

#-------------------------------------------------------------------------------

def lno(id):
    """
    This function returns the source file line number of the caller.
    """

    from inspect import currentframe

    cf = currentframe()
    return '%s-%05d' % (id, cf.f_back.f_lineno)

#-------------------------------------------------------------------------------

def manage_group_users(config, tables, group, users, option=None):
    """
    Ensure all the specified users and only the specified users are
    members of the specified group. The specified group and users
    have all been pre-verified.
    """

    table = 'csv2_user_groups'

    # if there is only one user, make it a list anyway
    if users:
        if isinstance(users, str):
            user_list = users.split(',')
        else:
            user_list = users
    else:
        user_list = []

    # Retrieve the list of users already in the group.
    db_users=[]

    where_clause = "group_name='%s'" % group
    rc, msg, user_groups_list = config.db_query(table, where=where_clause)

    for row in user_groups_list:
        db_users.append(row['username'])

    if not option or option == 'add':
        # Get the list of users specified that are not already in the group.
        add_users = diff_lists(user_list, db_users)

        # Add the missing users.
        for user in add_users:
            user_dict = {
                "username": user,
                "group_name": group
            }
            rc, msg = config.db_insert(table, user_dict)
            if rc != 0:
                return 1, msg

    if not option:
        # Get the list of users that the group currently has but were not specified.
        remove_users = diff_lists(db_users, user_list)
        
        # Remove the extraneous users.
        for user in remove_users:
            user_dict = {
                "username": user,
                "group_name": group
            }
            rc, msg = config.db_delete(table, user_dict)
            if rc != 0:
                return 1, msg

    elif option == 'delete':
        # Get the list of users that the group currently has and were specified.
        remove_users = diff_lists(user_list, db_users, option='and')
        
        # Remove the extraneous users.
        for user in remove_users:
            user_dict = {
                "username": user,
                "group_name": group
            }
            rc, msg = config.db_delete(table, user_dict)
            if rc != 0:
                return 1, msg

    return 0, None

#-------------------------------------------------------------------------------

def manage_user_groups(config, tables, user, groups, option=None):
    """
    Ensure all the specified groups and only the specified groups are
    have the specified user as a member. The specified user and groups
    have all been pre-verified.
    """

    table = 'csv2_user_groups'

    # if there is only one group, make it a list anyway
    if groups:
        if isinstance(groups, str):
            group_list = groups.split(',')
        else:
            group_list = groups
    else:
        group_list = []

    # Retrieve the list of groups the user already has.
    db_groups=[]
    
    where_clause="username='%s'" % user
    rc, msg, user_groups_list = config.db_query(table, where=where_clause)

    for row in user_groups_list:
        db_groups.append(row['group_name'])

    if not option or option == 'add':
        # Get the list of groups specified that the user doesn't already have.
        add_groups = diff_lists(group_list, db_groups)

        # Add the missing groups.
        for group in add_groups:
            user_grp_dict = {
                "username": user,
                "group_name": group
            }
            rc, msg = config.db_insert(table, user_grp_dict)
            if rc != 0:
                return 1, msg

    if not option:
        # Get the list of groups that the user currently has but were not specified.
        remove_groups = diff_lists(db_groups, group_list)
        
        # Remove the extraneous groups.
        for group in remove_groups:
            user_grp_dict = {
                "username": user,
                "group_name": group
            }
            rc, msg = config.db_delete(table, user_grp_dict)
            if rc != 0:
                return 1, msg

    elif option == 'delete':
        # Get the list of groups that the user currently has and were specified.
        remove_groups = diff_lists(group_list, db_groups, option='and')
        
        # Remove the extraneous groups.
        for group in remove_groups:
            user_grp_dict = {
                "username": user,
                "group_name": group
            }
            rc, msg = config.db_delete(table, user_grp_dict)
            if rc != 0:
                return 1, msg

    return 0, None

#-------------------------------------------------------------------------------

def manage_user_group_verification(config, tables, users, groups):
    """
    Make sure the specified users and groups exist.
    """

    if users:
        # if there is only one user, make it a list anyway
        if isinstance(users, str):
            user_list = users.split(',')
        else:
            user_list = users

        # Get the list of valid users.
        table = 'csv2_user'
        rc, msg, db_user_list = config.db_query(table)

        valid_users = {}
        for row in db_user_list:
            valid_users[row['username']] = False

        # Check the list of specified users.
        for user in user_list:
            if user not in valid_users:
                return 1, 'specified user "%s" does not exist' % user
            elif valid_users[user]:
                return 1, 'user "%s" was specified twice' % user
            else:
                valid_users[user] = True


    if groups:
        # if there is only one group, make it a list anyway
        if isinstance(groups, str):
            group_list = groups.split(',')
        else:
            group_list = groups

        # Get the list of valid groups.
        table = 'csv2_groups'
        rc, msg, db_group_list = config.db_query(table)

        valid_groups = {}
        for row in db_group_list:
            valid_groups[row['group_name']] = False

        # Check the list of specified groups.
        for group in group_list:
            if group not in valid_groups:
                return 1, 'specified group "%s" does not exist' % group
            elif valid_groups[group]:
                return 1, 'group "%s" was specified twice' % group
            else:
                valid_groups[group] = True

    return 0, None

#-------------------------------------------------------------------------------

def qt(query, keys=None, prune=[], filter=None, convert=None):
    """
    Query Transform takes a list of dictionaries (eg. the result of an SqlAlchemy query)
    and transforms it into a standard python list (repeatably iterable). In the process,
    it can make the following transformations:

        o It can filter rows based on the result of an evaluated string; True is
          retained, and False is dropped.

        o It can delete columns from the rows (prune=[col1, col2,..]).

        o It can convert column values from rows (convert={'col1': 'datetime', ...}).

        o For a list of primary keys, it can sum a list of columns. For example, given
          the following "keys" specification:

            keys = {
                'primary': ['group_name', 'cpus'],
                'sum': ['slots', 'test']
                }

          and the following queryset (note the mixture of integers, floats, and strings):

            [
                {'group_name': 'atlas', 'cloud_name': 'cloud9', 'cpus': 1, 'slots': 8, 'test': 1.0},
                {'group_name': 'atlas', 'cloud_name': 'cloud9', 'cpus': 8, 'slots': 8, 'test': 2.9},
                {'group_name': 'testing', 'cloud_name': 'cloud9', 'cpus': 1, 'slots': '8', 'test': '3.8'},
                {'group_name': 'testing', 'cloud_name': 'cloud9', 'cpus': 2, 'slots': '4', 'test': '4.7'},
                {'group_name': 'testing', 'cloud_name': 'cloud9', 'cpus': 4, 'slots': '2', 'test': '5.6'},
                {'group_name': 'testing', 'cloud_name': 'cloud9', 'cpus': 8, 'slots': '1', 'test': '6.5'},
                {'group_name': 'testing', 'cloud_name': 'otter', 'cpus': 1, 'slots': 8, 'test': 7.4},
                {'group_name': 'testing', 'cloud_name': 'otter', 'cpus': 2, 'slots': 4, 'test': 8.3},
                {'group_name': 'testing', 'cloud_name': 'otter', 'cpus': 4, 'slots': '2', 'test': '9.2'},
                {'group_name': 'testing', 'cloud_name': 'otter', 'cpus': 8, 'slots': '1', 'test': '0.1'},
            ]

          would produce the following results:

            [
                {'group_name': 'atlas', 'cpus': 1, 'slots': 8, 'test': 1.0},
                {'group_name': 'atlas', 'cpus': 8, 'slots': 8, 'test': 2.9},
                {'group_name': 'testing', 'cpus': 1, 'slots': 16, 'test': 11.2},
                {'group_name': 'testing', 'cpus': 2, 'slots': 8, 'test': 13.0},
                {'group_name': 'testing', 'cpus': 4, 'slots': 4, 'test': 14.8},
                {'group_name': 'testing', 'cpus': 8, 'slots': 2, 'test': 6.6}
            ]
          
          NOTE: Numeric summation columns can either be integer or float or a 
                character string that can be converted by int() or float(). The
                result of summation is always an integer or a float.

        o It can split the query into a list and corresponding dictionaries (
          (keys={ 'primary': [...], 'secondary': [...], 'match_list': [...]).

          when the keys parameter specifies both a 'primary' and 'secondary' key
          lists (and optionally, a 'match_list'), the input query, must contain
          all primary and secondary keys. For each row in the queryset, qt uses
          the two key lists as follows:
  
          * For all keys in the primary list and any other key in the query not 
            mentioned in the secondary list, qt copies the values from the query
            into the primary output list.

          * For all keys in the primary list, plus the first key in the secondary
            list, qt creates a multi-level, nested output dictionary and copies
            the values for all secondary keys from the query into the lowest level
            dictionary.

          The 'match_list' is both a switch (requesting additional processing) and
          complimantary input. It causes qt to generate and return a multi-level
          nested dictionary/list of all secondary key values per compound primary
          key. The match list must contain all the primary keys and is used to
          build an empty structure with all possible compound privary key values.
          Subsequently, qt scans the secondary dictionary extracting the secondary
          keys to be listed.
        
          A practical example of list splitting can be found in user_views.py, which
          does the following:
        
          # Retrieve the user list but loose the passwords.
          s = select([view_user_groups])
          user_list = qt(config.db_connection.execute(s), prune=['password'])

          # Retrieve user/groups list (dictionary containing list for each user).
          s = select([csv2_user_groups])
          ignore1, ignore2, groups_per_user = qt(
              config.db_connection.execute(s),
              keys = {
                  'primary': [
                      'username',
                      ],
                  'secondary': [
                      'group_name',
                      ],
                  'match_list': user_list,
                  }
              )

          # Retrieve  available groups list (dictionary containing list for each user).
          s = select([view_user_groups])
          ignore1, ignore2, available_groups_per_user = qt(
              config.db_connection.execute(s),
              keys = {
                  'primary': [
                      'username',
                      ],
                  'secondary': [
                      'group_name',
                      'available',
                      ],
                  'match_list': user_list,
                  }
              )

        o For a list of primary keys, it creates nested dictionaries. For example, given
          the following "keys" specification:

            keys = {
                'primary': ['group_name', 'flavor']
                }

          and the following queryset:

          {'group_name': 'test-dev2', 'cloud_name': 'lrz2', 'flavor': 'lrz2:tiny', 'authurl': 'https://cc.lrz.de:5000/v3', 'flavor_slots': 1}
          {'group_name': 'test-dev2', 'cloud_name': 'lrz2', 'flavor': 'lrz2:lrz.small', 'authurl': 'https://cc.lrz.de:5000/v3', 'flavor_slots': 1}
          {'group_name': 'testing', 'cloud_name': 'otter', 'flavor': 'otter:s1', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 3}
          {'group_name': 'testing', 'cloud_name': 'otter', 'flavor': 'otter:s2', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 1}
          {'group_name': 'testing', 'cloud_name': 'otter', 'flavor': 'otter:s3', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 1}

          qt would produce the following results:

          {
              'test-dev2': {
                      'lrz2:tiny':      { 'cloud_name': 'lrz2', 'authurl': 'https://cc.lrz.de:5000/v3', 'flavor_slots': 1 },
                      'lrz2:lrz.small': { 'cloud_name': 'lrz2', 'authurl': 'https://cc.lrz.de:5000/v3', 'flavor_slots': 1 }
                  },
              'testing': {
                  'otter:s1':           { 'cloud_name': 'otter', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 3},
                  'otter:s2':           { 'cloud_name': 'otter', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 1},
                  'otter:s3':           { 'cloud_name': 'otter', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 1}
                  },
              }

          Note: If the list of primary keys results in duplicate entries, the inner-most nested dictionary will contain the last row for the composite
          key.  For example, given the previouse queryset and a primary key specification of "['group_name', 'cloud_name']". the result would have been:

          {
              'test-dev2': {
                      'lrz2':           { 'flavor': 'lrz2:lrz2.small', 'authurl': 'https://cc.lrz.de:5000/v3', 'flavor_slots': 1 }
                  },
              'testing': {
                  'otter':              { 'flavor': 'otter:s3', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 1}
                  },
              }
          
          If you want to retain all rows, keys must also specify "'list_duplicates': True", in which case, the inner most dictionary is replaced by a
          list of dictionaries. For example, given the previouse queryset and a primary key specification of:

            keys = {
                'primary': ['group_name', 'cloud_name'],
                'list_duplicates': True
                }

          the result would have been:

          {
              'test-dev2': {
                      'lrz2': [
                          {'flavor': 'lrz2:tiny', 'authurl': 'https://cc.lrz.de:5000/v3', 'flavor_slots': 1},
                          {'flavor': 'lrz2:lrz.small', 'authurl': 'https://cc.lrz.de:5000/v3', 'flavor_slots': 1}
                          ]      
                  },
              'testing': {
                  'otter': [
                          {'flavor': 'otter:s1', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 3},
                          {'flavor': 'otter:s2', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 1},
                          {'flavor': 'otter:s3', 'authurl': 'https://otter.heprc.uvic.ca:5000/v3', 'flavor_slots': 1}
                          ]      
                  },
              }
          
    """

    if keys and not ( ('primary' in keys and len(keys.keys()) == 1) or \
        ('primary' in keys and 'list_duplicates' in keys) or \
        ('primary' in keys and 'sum' in keys) or \
        ('primary' in keys and 'secondary' in keys) ):

        raise Exception('view_utils.qt: "keys" dictionary requires either a "primary" specification or a "primary/sum" specification or a "primary/secondary" specification.')
    elif keys and 'match_list' in keys and 'secondary' not in keys:
        raise Exception('view_utils.qt: "keys" dictionary requires a "primary/secondary" specification if "match_list" is also specified.')

    from decimal import Decimal
#   from view_utils import _qt, _qt_list, _qt_list_sum
    import time

    # Initialize return structures.
    primary_list = []
    secondary_dict = {}
    matched_dict = {}

    # Handle an null query.
    if query:
        Query = query
    else:
        Query = []

    # Process query rows.
    for row in Query:
        # If specified, apply the row filter.
        if filter:
            cols = dict(row)
            if not eval(filter):
                continue

        # Prune and convert columns.
        cols = {}
        for col in row:
            if col not in prune:
                if convert and col in convert and row[col] != None:
                    if convert[col] == 'datetime':
                        cols[col] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dict(row)[col]))
                else:
                    cols[col] = dict(row)[col]

        if not keys:
            primary_list.append(cols)

        elif keys and 'primary' in keys and 'sum' in keys:
            secondary_dict_ptr = secondary_dict
            for key in keys['primary']:
                ignore, secondary_dict_ptr = _qt(False, secondary_dict_ptr, cols, key)

            for col in keys['sum']:
                # Special case for clouds which are disabled:
                if 'enabled' in cols and 'VMs' in cols:
                    if cols['VMs'] > 0:
                        enabled = 1
                    else:    
                        enabled = cols['enabled']
                else:
                    enabled = 1

                if col in cols and enabled == 1:
                    if col not in secondary_dict_ptr:
                        secondary_dict_ptr[col] = 0

                    if isinstance(cols[col], int):
                        secondary_dict_ptr[col] += cols[col]
                    elif isinstance(cols[col], float):
                        secondary_dict_ptr[col] = float(Decimal(str(secondary_dict_ptr[col])) + Decimal(str(cols[col])))
                    else:
                        try:
                            secondary_dict_ptr[col] += int(cols[col])
                        except:
                            try:
                                secondary_dict_ptr[col] = float(Decimal(str(secondary_dict_ptr[col])) + Decimal(cols[col]))
                            except:
                                pass

        elif keys and 'primary' in keys and 'secondary' in keys:
            add_row = False
            secondary_dict_ptr = secondary_dict
            for key in keys['primary']:
                add_row, secondary_dict_ptr = _qt(add_row, secondary_dict_ptr, cols, key)
             
            if keys['secondary']:
                ignore, secondary_dict_ptr = _qt(False, secondary_dict_ptr, cols, keys['secondary'][0])
            
            for col in cols:
                if col in keys['secondary'] and cols[col]:
                    secondary_dict_ptr[col] = cols[col]
            
            if add_row:
                new_row = {}
                for col in cols:
                    if col not in keys['secondary']:
                        new_row[col] = cols[col]


                primary_list.append(new_row)

        elif keys and 'primary' in keys:
            def set_ptr(ptr, cols, key, list):
                if cols[key] not in ptr:
                   if list:
                       ptr[cols[key]] = []
                   else:
                       ptr[cols[key]] = {}

                return ptr[cols[key]]

            if 'list_duplicates' in keys and keys['list_duplicates']:
                secondary_dict_ptr = secondary_dict
                for ix in range(len(keys['primary'])):
                    secondary_dict_ptr = set_ptr(secondary_dict_ptr, cols, keys['primary'][ix], ix==len(keys['primary'])-1)

                secondary_dict_ptr.append({})
                for col in cols:
                    secondary_dict_ptr[-1][col] = cols[col]

            else:
                secondary_dict_ptr = secondary_dict
                for key in keys['primary']:
                    secondary_dict_ptr = set_ptr(secondary_dict_ptr, cols, key, False)

                for col in cols:
                    secondary_dict_ptr[col] = cols[col]

    if not keys:
        return primary_list

    elif keys and 'primary' in keys and 'sum' in keys:
         _qt_list_sum(primary_list, {}, secondary_dict, keys['primary'], 0)
         return primary_list

    elif keys and 'primary' in keys and 'secondary' in keys:
        if 'match_list' in keys:
            for row in keys['match_list']:
                matched_dict_ptr = matched_dict
                for key in keys['primary'][:-1]:
                    add_row, matched_dict_ptr = _qt(add_row, matched_dict_ptr, row, key)

                matched_dict_ptr[row[keys['primary'][-1]]] = []

            secondary_dict_ptr = secondary_dict
            matched_dict_ptr = matched_dict

            for secondary_key1 in secondary_dict_ptr:
                if secondary_key1 not in matched_dict_ptr:
                    matched_dict_ptr[secondary_key1] = []

                for secondary_key2 in secondary_dict_ptr[secondary_key1]:
                    matched_dict_ptr[secondary_key1].append(secondary_key2)

            return primary_list, secondary_dict, matched_dict
        else:
            return primary_list, secondary_dict

    elif keys and 'primary' in keys:
        return secondary_dict

#-------------------------------------------------------------------------------

def _qt(add_row, secondary_dict_ptr, cols, key):
    """
    This sub-function is called by view_utils.qt to add keys to the secondary_dict and
    is NOT meant to be called directly.
    """

    if cols[key]:
        if cols[key] in secondary_dict_ptr:
            return add_row, secondary_dict_ptr[cols[key]]
        else:
            secondary_dict_ptr[cols[key]] = {}
            return True, secondary_dict_ptr[cols[key]]
    else:
        return add_row, secondary_dict_ptr

#-------------------------------------------------------------------------------

def _qt_list(secondary_dict_ptr, secondary_key_list_ptr, cols, key):
    """
    This sub-function is called by view_utils.qt to add keys to the secondary_key_list and
    is NOT meant to be called directly.
    """

    if cols[key]:
        if cols[key] not in secondary_key_list_ptr:
            secondary_key_list_ptr[cols[key]] = {}

        return secondary_dict_ptr[cols[key]], secondary_key_list_ptr[cols[key]]
    else:
      return secondary_dict_ptr, secondary_key_list_ptr

#-------------------------------------------------------------------------------

def _qt_list_sum(primary_list, primary_dict_parent, secondary_dict_ptr, key_list, ix):
    """
    This sub-function is called by view_utils.qt to list a queryset's sums.
    It is NOT meant to be called directly.
    """

    if len(secondary_dict_ptr) > 0 and isinstance(secondary_dict_ptr[list(secondary_dict_ptr)[0]], dict) :
        for key in secondary_dict_ptr:
            primary_dict = dict(primary_dict_parent)
            primary_dict.update({key_list[ix]: key})
            _qt_list_sum(primary_list, primary_dict, secondary_dict_ptr[key], key_list, ix+1)

    else:
        primary_list.append(primary_dict_parent)
        primary_list[-1].update(secondary_dict_ptr)

#-------------------------------------------------------------------------------

def qt_filter_get(columns, values, aliases=None, and_or='and'):
    """
    Return an eveluation string to filter the rows of a queryset. This function takes the
    following arguments:
        o "columns" is a list of columns to be matched against items within the "values"
           parameter.

        o "values" is either a list or a dictionary. If it is a dictionary, the keys are
          column names identified by the columns parameter. If it is a list, the values 
          in the list have an index value corresponding to the columns argument. A value
          for a column can have one of five formats:
              1. An integer.
              2. A string. A string of "null" will match column is null.
              3. A string containing a comma separated list.
              4. A list.
              5. An alias ("aliases" parameter required, see below). Each alias is 
                 replaced by its corresponding value.

        o "aliases" is a structure with the following format:
              aliases = {
                  <column_name_1>: {
                      <alias_1>: <value>,
                      <alias_2>: <value>,
                       . 
                      },
                  <column_name_2>: {
                      <alias_1>: <value>,
                      <alias_2>: <value>,
                       . 
                      },
                   .
                  }

          The "value" for an alias can be any one of the first four formats. 

        o "and_or" is either "and" default) or "or" and is used as the boolean operator
          between column selections.
    """

    key_value_list = []
    for ix in range(len(columns)):
        if isinstance(values, dict):
            if columns[ix] in values:
                value = values[columns[ix]]
            else:
                continue

        else:
            if ix < len(values):
                value = values[ix]
            else:
                break

        if value == '':
            continue

        if aliases and columns[ix] in aliases and value in aliases[columns[ix]]:
            value = aliases[columns[ix]][value]

        try:
            x = float(value)
            key_value_list.append("cols['%s'] == %s" % (columns[ix], value))
        except:
            if isinstance(value, list):
                key_value_list.append("cols['%s'] in %s" % (columns[ix], value))
            elif value == 'null':
                key_value_list.append("cols['%s'] is null" % columns[ix])
            elif ',' in value:
                key_value_list.append("cols['%s'] in %s" % (columns[ix], value.split(',')))
            else:
              key_value_list.append("cols['%s'] == '%s'" % (columns[ix], value))

    if len(key_value_list) < 1:
        return None
    else:
        return (' %s ' % and_or).join(key_value_list)

#-------------------------------------------------------------------------------

def render(request, template, context):
    """
    If the "Accept" HTTP header contains "application/json", return a json string. Otherwise,
    return an HTML string.
    """

    from django.shortcuts import render as django_render
    from django.http import HttpResponse
    import datetime
    import decimal
    import json

    class csv2Encoder(json.JSONEncoder):
        def default(self, obj):
            if str(obj.__class__).split("'")[1].split('.')[0] == 'sqlalchemy':
                return str(obj)

            if isinstance(obj, datetime.date):
                return str(obj)

            if isinstance(obj, decimal.Decimal):
                return str(obj)

            if isinstance(obj, dict) and 'ResultProxy' in obj:
                return json.dumps(obj['ResultProxy'])

            if isinstance(obj, Query):
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' ]:
                    data = obj.__getattribute__(field)
                    try:
                        json.dumps(data) # this will fail on non-encodable values, like other classes
                        fields[field] = data
                    except TypeError:
                        fields[field] = None
                # a json-encodable dict
                return json.dumps(fields)

            return json.JSONEncoder.default(self, obj)

    if request.META['HTTP_ACCEPT'] == 'application/json':
        response = HttpResponse(json.dumps(context, cls=csv2Encoder), content_type='application/json')
    else:
        response = django_render(request, template, context)
    end_time = time.time()
    print("Render time: %f.5" % end_time)
    return response

#-------------------------------------------------------------------------------

def service_msg(service_name):
    
    import os

    return os.popen("service "+service_name+" status | grep 'Active' | cut -c12-").read()    

#-------------------------------------------------------------------------------
# this function gets and sets the user groups for the active user as well as authenticates the active user
# if super_user is true and the requesting user doesn't have super user status a permission denied is raised
# if super user is false then skip the check for super user
#-------------------------------------------------------------------------------
def set_user_groups(config, request, super_user=True):

    class active_user:
        def __init__(self, config, request):
            remote_user = request.META.get('REMOTE_USER')
            table = "view_user_groups"

            where_clause = "username='%s' or cert_cn='%s'" % (remote_user, remote_user)
            rc, msg, csv2_user = config.db_query(table, where=where_clause)

            user = None
            for user in csv2_user:
                self.username = user['username']
                self.cert_cn = user['cert_cn']
                self.is_superuser = user['is_superuser']
                self.join_date = user['join_date']
                self.active_group = '-'
                self.default_group = user['default_group']

                if user['user_groups'] and len(user['user_groups']) > 0:
                    self.user_groups = user['user_groups'].split(',')
                else:
                    self.user_groups = []

                if user['available_groups'] and len(user['available_groups']) > 1:
                    self.available_groups = user['available_groups'].split(',')
                else:
                    self.available_groups = []

                self.flag_global_status = user['flag_global_status']
                self.flag_jobs_by_target_alias = user['flag_jobs_by_target_alias']
                self.flag_show_foreign_global_vms = user['flag_show_foreign_global_vms']
                self.flag_show_slot_detail = user['flag_show_slot_detail']
                self.flag_show_slot_flavors = user['flag_show_slot_flavors']
                self.status_refresh_interval = user['status_refresh_interval']

                self.args = []
                self.kwargs = {}
                break

            if not user:
                raise PermissionDenied

            if request.method == 'GET':
                for key_val in request.META.get('QUERY_STRING').split('&'):
                    if len(key_val) > 0:
                        words = key_val.split('=', 1)
                        if len(words) > 1:
                            self.kwargs[words[0].strip()] = words[1].strip()
                        else:
                            self.args.append(words[0].strip())

            elif request.method == 'POST' and 'group' in request.POST:
                self.args.append(request.POST['group'])
               

    new_active_user = active_user(config, request)

    if super_user and not new_active_user.is_superuser:
        raise PermissionDenied

    if len(new_active_user.user_groups) < 1:
#       return 1,'user "%s" is not a member of any group.' % new_active_user.username, new_active_user, new_active_user.user_groups
        return 1,'user "%s" is not a member of any group.' % new_active_user.username, new_active_user

    if len(new_active_user.args) > 0:
        new_active_user.active_group = new_active_user.args[0]
    elif new_active_user.default_group and new_active_user.default_group in new_active_user.user_groups:
        new_active_user.active_group = new_active_user.default_group
    else:
        new_active_user.active_group = new_active_user.user_groups[0]
    
    if new_active_user.active_group not in new_active_user.user_groups:
#       return 1,'cannot switch to invalid group "%s".' % new_active_user.active_group, new_active_user, new_active_user.user_groups
        return 1,'cannot switch to invalid group "%s".' % new_active_user.active_group, new_active_user

#   return 0, None, new_active_user, new_active_user.user_groups
    return 0, None, new_active_user

#-------------------------------------------------------------------------------

def table_fields(Fields, Table, Columns, selection):
    """
    This function returns input fields for the specified table.

    Arguments:

    Table    - Is a table string as returned by validate_fields.

    Columns  - Are the primary and secondary column lists for tables
               as returned by validate_fields.

    Fields   - Is a dictionary of input fields as returned by
               validate_fields.
    """

    output_fields = {}

    if selection == 'insert':
        for field in Columns[Table][0]:
            if field in Fields:
                output_fields[field] = Fields[field]

    if selection == 'insert' or selection == 'update':
        for field in Columns[Table][1]:
            if field in Fields:
                output_fields[field] = Fields[field]

    return output_fields

#-------------------------------------------------------------------------------

def validate_by_filtered_table_entries(config, value, field, table_name, column_name, filter_list, allow_value_list=False):
    """
    This function validates that a value is present in a filtered table column
    
    Arguments:

    value       - the value or list of values (see allow_value_list option) to be validated.
    field       - the name of the field being validated(for error message only).
    table_name  - the name of the table.
    column_name - then name of the column.
    filter_list - the list of filters in the following format:

                  [[col1, val1], [col2, val2], ...]
    """

    #import cloudscheduler.lib.schema_na as schema

    table = table_name

    options = []
    where = False
    where_string = ""
    for filter in filter_list:
        if len(filter) != 2:
            return 1, 'incorrect filter format'
        if len(where_string)==0:
            where_string = "%s='%s'" % (filter[0], filter[1])
        else:
            where_string = where_string + " and %s='%s'" % (filter[0], filter[1])
        if where is False:
            where = True

    rc, msg, rows = config.db_query(table, where=where_string)
    for row in rows:
        if column_name in row and (not row[column_name] in options):
            options.append(row[column_name])

    if allow_value_list:

        if isinstance(value, str):
            values = value.split(',')
        else:
            values = value

        for val in values:
            if val not in options:
                msg = 'specified value in list of values does not exist: {}={}'.format(field, val)
                for filter in filter_list:
                    msg += ', {}={}'.format(filter[0], filter[1])
                return 1, msg
        return 0, None
    else:
        if value in options:
            return 0, None
        else:
            msg = 'specified item does not exist: {}={}'.format(field, value)
            for filter in filter_list:
                msg += ', {}={}'.format(filter[0], filter[1])
            return 1, msg

#-------------------------------------------------------------------------------

def validate_fields(config, request, fields, tables, active_user):
    """
    This function validates/normalizes form fields/command arguments.

    Arguments:

    config    - A configuration object.
    requests  - is a web request containing POST data.
    tables    - is a list of table names.
    fields    - is a  list of structures in the following format:

               CLOUD_FIELDS = {
                   'auto_active_group': active_user.active_group, # or None.
                   'format': {
                       'cloud_name': 'lowerdash',
                       'group_name': 'lowerdash',

                       'cores_slider': 'ignore',
                       'csrfmiddlewaretoken': 'ignore',
                       'group': 'ignore',
                       'ram_slider': 'ignore',
                       },
                   }


    Possible format strings are:

    ['opt1', 'opt2', ...]  - A list of valid options.
    ('table', 'column', <False/True>, <False/True>) - A list of valid options derrived from the
                             named table and column.  If the first optional boolean column is set
                             to True, then a comma seperated list of values will be validated. If
                             the second optional boolean column is set to True, then an empty
                             string (null value) can be accepted.
    {"argN": "<type>", .... "options": {"optN": "<type>" ....}
                           - is a json dictionary string defining the format of a json dictionary
                             parameter. All "args" are mandatory, all "opts" are optional, 
                             everything else is invalid. Valid "<types>" include: string, integer,
                             boolean, float, etc.
    boolean                - A value of True or False will be inserted into the output fields.
    dboolean               - Database boolean values are either 0 or 1; allow and
                             convert true/false/yes/no/on/off.
    float                  - A floating point value.
    ignore                 - Ignore missing mandatory fields or fields for undefined columns.
    integer                - An integer value.
    lower                  - Ensure that the input value consists only of lowercase letters, digits,
                             dashes, underscores, periods, and colons; does not contain '--'; and
                             does not start or end with a dash (or error).
    metadata               - Identifies a pair of fields (eg. "xxx' and xxx_name) that contain ar
                             metadata string and a metadata filename. If the filename conforms to
                             pre-defined patterns (eg. ends with ".yaml"), the string will be 
                             checked to conform with the associated file type.
    password               - A password value to be checked and hashed
    password1              - A password value to be verified against password2, checked and hashed.
    password2              - A password value to be verified against password1, checked and hashed.
    reject                 - Reject an otherwise valid field.
    upper                  - Ensure that the input value consists only of uppercase letters, digits,
                             dashes, underscores, periods, and colons; does not contain '--'; and
                             does not start or end with a dash (or error).

    POSTed fields in the form "name.1", "name.2", etc. will be treated as array fields, 
    returning the variable "name" as a list of strings. 

    """

    from .view_utils import _validate_fields_pw_check
    #import cloudscheduler.lib.schema_na as schema
    import ipaddress
    import json
    import re
    import socket

    # Retrieve relevant (re: tables) schema.
    all_columns = []
    primary_key_columns = []
    Tables = {}
    Columns = {}
    for table_option in tables:
        table = table_option.split(',')
        
        try:
            Tables[table[0]] = schema[table[0]]
        except:
            raise Exception('view_utils.validate_fields: "tables" parameter contains an invalid table name "%s" not defined in schema.py.' % table[0])
            
        # Not sure what this is for -Colson oct 7 2020
        if len(table) > 1 and table[1] == 'n':
            continue

        Columns[table[0]] = [[], []]
        #loop thru keys
        for column_name in Tables[table[0]]['keys']:
            if column_name not in all_columns:
                all_columns.append(column_name)
            primary_key_columns.append(column_name)

        #loop thru other columns:
        for column_name in Tables[table[0]]['columns']:
            if column_name not in all_columns:
                all_columns.append(column_name)
            Columns[table[0]][1].append(column_name)

    # Process fields parameter:
    Formats = {}
    Mandatory = []
    AllowEmpty = []
    NotEmpty = []
    ArrayFields = []
    Options = {
        'accept_primary_keys_only': False,
        'auto_active_group': False,
        'auto_active_user': False,
        'unnamed_fields_are_bad': False,
        }

    for option_set in fields:
        for option in option_set:
            if option == 'format':
                for field in option_set[option]:
                    Formats[field] = option_set[option][field]
            elif option == 'mandatory':
                if isinstance(option_set[option], list):
                    Mandatory += option_set[option]
                else:
                    Mandatory.append(option_set[option])
            elif option == 'allow_empty':
                if isinstance(option_set[option], list):
                    AllowEmpty += option_set[option]
                else:
                    AllowEmpty.append(option_set[option])
            elif option == 'not_empty':
                if isinstance(option_set[option], list):
                    NotEmpty += option_set[option]
                else:
                    NotEmpty.append(option_set[option])
            elif option == 'array_fields':
                if isinstance(option_set[option], list):
                    ArrayFields += option_set[option]
                else:
                    ArrayFields.append(option_set[option])
            else:
                Options[option] = option_set[option]

    # Process input fields.
    Fields = {}
    if request.method == 'POST':
        for field in sorted(request.POST):
            if field == 'group':
                continue

            if Options['accept_primary_keys_only'] and field not in primary_key_columns:
                if not (field in Formats and Formats[field] == 'ignore'):
                    return 1, 'request contained superfluous parameter "%s".' % field, None, None, None
            if Options['unnamed_fields_are_bad'] and field not in Formats:
                return 1, 'request contained a unnamed/bad parameter "%s".' % field, None, None, None

            field_alias = field
            value = request.POST[field]

            if field in Formats:
                if isinstance(Formats[field], (list, tuple)):
                    if isinstance(Formats[field], tuple):
                        options = []
                        # not clear what this select is supposed to be hitting
                        # if cloudscheduler.lib.schema.__dict__[Formats[field][0]] resolves to a table name in schema_na.py it should be fine

                        table_name = Formats[field][0]
                        rc, msg, rows = config.db_query(table_name, distinct=True)
                        for row in rows:
                           if Formats[field][1] in row and (not row[Formats[field][1]] in options):
                              options.append(row[Formats[field][1]])
                    else:
                        options = Formats[field]

                    good_value = True
                    print("Good value: F:%s, O:%s" % (Formats[field][1], options))

                    if isinstance(Formats[field], tuple) and len(Formats[field]) > 2 and Formats[field][2]:
                        if len(Formats[field]) > 3 and Formats[field][3] and value == '':
                            value = None
                        else:
                            values = []
                            lower_values = value.lower().split(',')
                            for lower_value in sorted(lower_values):
                                for ix in range(len(options)+1):
                                    if ix < len(options):
                                        if lower_value == str(options[ix]).lower():
                                            values.append(str(options[ix]))
                                            break
                                    else:
                                        good_value = False

                            if good_value:
                                value = ','.join(values)

                    else:
                        lower_value = value.lower()
                        for ix in range(len(options)+1):
                            if ix < len(options):
                                if lower_value == str(options[ix]).lower():
                                    value = str(options[ix])
                                    break
                            else:
                                good_value = False

                    if not good_value:
                        return 1, 'value specified for "%s" must be one of the following options: %s.' % (field, sorted(options)), None, None, None

                elif isinstance(Formats[field], dict):
                    def check_value_type(value, fmt):
                        if fmt == 'integer':
                            return isinstance(value, int)
                        elif fmt == 'boolean':
                            return isinstance(value, bool)
                        elif fmt == 'float':
                            return isinstance(value, float)
                        elif fmt == 'string':
                            return isinstance(value, str)
                        return False

                    try:
                        value_dict = json.loads(value)
                    except:
                        return 1, 'value specified for "%s" must be a valid JSON string.' % field, None, None, None

                    if value_dict is not None and not isinstance(value_dict, dict):
                        return 1, 'JSON string value specified for "%s" must contain a dictionary or be "null".' % field, None, None, None

                    if value_dict is None:
                        value = None

                    else:
                        awol_keys = []
                        bad_keys = []
                        bad_vals = []
                        mand_keys = []
                        min_pick = 1
                        opt_keys = []
                        pick_keys = []
                        picked_keys = []
                        for mkey in Formats[field]:
                            if mkey == 'options':
                                for okey in Formats[field]['options']:
                                    opt_keys.append(okey)
                            elif mkey == 'min_pick':
                                if check_value_type(Formats[field]['min_pick'], 'integer'):
                                    min_pick = Formats[field]['min_pick']
                                else:
                                    bad_vals.append('%s: %s(%s)' % (mkey, Formats[field][mkey], type(value_dict[mkey])))
                            elif mkey == 'pick':
                                for pkey in Formats[field]['pick']:
                                    pick_keys.append(pkey)
                            else:
                                mand_keys.append(mkey)
                                if mkey not in value_dict:
                                    awol_keys.append(mkey)

                        for key in value_dict:
                            if key in mand_keys:
                                if not check_value_type(value_dict[key], Formats[field][key]):
                                    bad_vals.append('%s: %s(%s)' % (key, Formats[field][key], type(value_dict[key])))
                            elif key in opt_keys:
                                if not check_value_type(value_dict[key], Formats[field]['options'][key]):
                                    bad_vals.append('%s: %s(%s)' % (key, Formats[field]['options'][key], type(value_dict[key])))
                            elif key in pick_keys:
                                if check_value_type(value_dict[key], Formats[field]['pick'][key]):
                                    picked_keys.append(key)
                                else:
                                    bad_vals.append('%s: %s(%s)' % (key, Formats[field]['pick'][key], type(value_dict[key])))
                            else:
                                bad_keys.append(key)

                        if len(awol_keys) > 0:
                            return 1, 'dictionary specified for "%s" is missing the following mandatory keys: %s' % (field, awol_keys), None, None, None

                        if len(bad_keys) > 0:
                            return 1, 'dictionary specified for "%s" contains the following undefined keys: %s' % (field, bad_keys), None, None, None

                        if len(bad_vals) > 0:
                            return 1, 'dictionary specified for "%s" contains the following key values of the wrong type: %s' % (field, bad_vals), None, None, None

                        if len(picked_keys) < min_pick:
                            return 1, 'At least %s of %s (%s) selectable keys are required for %s; dictionary specified only %s (%s) keys.' % (min_pick, len(pick_keys), pick_keys, field, len(picked_keys), picked_keys), None, None, None

                elif Formats[field][:4] == 'fqdn':
                    words = Formats[field].split(',')
                    if value == '':
                        value = None
                        if len(words) > 1:
                            Fields[words[1]] = 0
                    else:
                        try:
                            current_hostname = socket.gethostbyname(value)
                            if len(words) > 1:
                                Fields[words[1]] = int(ipaddress.IPv4Address(current_hostname))
                        except Exception as exc:
                            return 1, 'The value specified for %s (%s) is not a valid FQDN.' % (field, value), None, None, None

                elif Formats[field] == 'dboolean':
                    lower_value = value.lower()
                    if lower_value == 'true' or lower_value == 'yes' or lower_value == 'on' or lower_value == '1':
                        value = 1
                    elif lower_value == 'false' or lower_value == 'no' or lower_value == 'off' or lower_value == '0':
                        value = 0
                    else:
                        return 1, 'boolean value specified for "%s" must be one of the following: true, false, yes, no, 1, or 0.' % field, None, None, None

                elif Formats[field] == 'float':
                    try:
                        float_value = float(value)
                    except:
                        return 1, 'value specified for "%s" must be a floating point value.' % field, None, None, None

                elif Formats[field] == 'integer':
                    try:
                        integer = int(value)
                    except:
                        return 1, 'value specified for "%s" must be an integer value.' % field, None, None, None

                elif Formats[field] == 'lowerdash':
                    if value == '' and field not in AllowEmpty:
                        return 1, 'value specified for "%s" must not be the empty string.' % field, None, None, None
                    if re.fullmatch("^(?!-)(?!.*--)[a-z0-9.:,-]*(?<!-)$", request.POST[field]):
                        value = request.POST[field]
                    else:
                        return 1, 'value specified for "%s" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.' % field, None, None, None

                elif Formats[field] == 'lowercase':
                    if re.fullmatch("([a-z0-9_.,:]-?)*[a-z0-9_.,:]", request.POST[field]) or request.POST[field] == '':
                        value = request.POST[field]
                    else:
                        return 1, 'value specified for "%s" must be all lower case.' % field, None, None, None

                elif Formats[field] == 'lowernull':
                    if re.fullmatch("([a-z0-9_.,:]-?)*[a-z0-9_.,:]", request.POST[field]):
                        value = request.POST[field]
                    elif request.POST[field] == '':
                        value = None
                    else:
                        return 1, 'value specified for "%s" must be all lower case.' % field, None, None, None

                elif Formats[field] == 'mandatory':
                    if value.strip() == '':
                        return 1, 'value specified for "%s" must not be an empty string.' % field, None, None, None

                elif Formats[field] == 'metadata':
                    filename = '%s_name' % field
                    if filename in request.POST:
                        # Verify yaml files.
                        if (len(request.POST[filename]) > 4 and request.POST[filename][-4:] == '.yml') or \
                            (len(request.POST[filename]) > 5 and request.POST[filename][-5:] == '.yaml'):

                            import yaml

                            try:    
                                temp_data = yaml.full_load(value)
                            except yaml.scanner.ScannerError as ex:
                                return 1, 'yaml value specified for "%s (%s)" is invalid - scanner error - %s' % (field, filename, ex), None, None, None
                            except yaml.parser.ParserError as ex:
                                return 1, 'yaml value specified for "%s (%s)" is invalid - parser error - %s' % (field, filename, ex), None, None, None
                            except Exception as ex:
                                return 1, 'yaml value specified for "%s (%s)" is invalid - unknown error - %s' % (field, filename, ex), None, None, None

                elif Formats[field] == 'password':
                    rc, value = _validate_fields_pw_check(request.POST[field])
                    if rc != 0:
                        return 1, value, None, None, None

                elif Formats[field] == 'password1':
                    field_alias = '%s2' % field[:-1]
                    pw2 = request.POST.get(field_alias)
                    if not pw2:
                        if not request.POST[field]:
                            continue
                        return 1, 'password update received a password but no verify password; both are required.', None, None, None

                    rc, value = _validate_fields_pw_check(request.POST[field],pw2=pw2)
                    if rc != 0:
                        return 1, value, None, None, None
                    field_alias = field[:-1]

                elif Formats[field] == 'password2':
                    field_alias = '%s1' % field[:-1]
                    if not request.POST.get(field_alias):
                        if not request.POST[field]:
                            continue
                        return 1, 'password update received a verify password but no password; both are required.', None, None, None
                    continue

                elif Formats[field] == 'reject':
                    return 1, 'request contained a rejected/bad parameter "%s".' % field, None, None, None

                elif Formats[field] == 'upper':
                    if field == '' and field not in AllowEmpty:
                        return 1, 'value specified for "%s" must not be the empty string.' % field, None, None, None
                        # Match the empty string or <a valid non-dash optionally followed by a dash> any number of times, followed by a valid non-dash.
                    elif re.fullmatch('(([A-Z0-9_.:]-?)*[A-Z0-9_.:])?', request.POST[field]):
                        value = request.POST[field]
                    else:
                        return 1, 'value specified for "%s" must be all uppercase letters, digits, dashes, underscores, periods, and colons, and cannot contain a more than one consecutive dash or start or end with a dash.' % field, None, None, None

            if field_alias in all_columns:
                Fields[field_alias] = value
            else: 
                array_field = field.split('.')
                if len(array_field) > 1 and array_field[0] in ArrayFields:
                    if array_field[0] not in Fields:
                        Fields[array_field[0]] = [value]
                    elif isinstance(Fields[array_field[0]], list):
                        Fields[array_field[0]].append(value)
                    else:
                        return 1, 'request contained parameter "%s" and parameter "%s".' % (field, array_field[0]), None, None, None
                else:
                    if field in Formats:
                        Fields[field] = value
                    else:
                        return 1, 'request contained a bad parameter "%s".' % field, None, None, None


        if Options['auto_active_group'] and 'group_name' not in Fields:
            Fields['group_name'] = active_user.active_group

        if Options['auto_active_user'] and 'username' not in Fields:
            Fields['username'] = active_user

        # Process booleans fields.
        for field in Formats:
            if Formats[field] == 'boolean':
                if request.POST.get(field):
                    if request.POST[field] == 'invalid-unit-test':
                        Fields[field] = 'invalid-unit-test'
                    else:
                        Fields[field] = True
                else:
                    Fields[field] = False

        for field in primary_key_columns + Mandatory:
            if field not in Fields and (field not in Formats or  Formats[field] != 'ignore'):
                return 1, 'request did not contain mandatory parameter "%s".' % field, None, None, None
#           if field in Fields and Fields[field] == '':
#               return 1, 'mandatory parameter "%s" contains an empty string which is specifically disallowed.' % field, None, None, None

        for field in NotEmpty:
            if field in request.POST:
                if Fields[field] == '' or Fields[field] is None:
                    return 1, 'parameter "%s" contains an empty string which is specifically disallowed.' % field, None, None, None
            #else:
            #    return 1, 'request did not contain mandatory (but not empty) parameter "%s".' % field, None, None, None

    return 0, None, Fields, Tables, Columns

#-------------------------------------------------------------------------------

def _validate_fields_pw_check(pw1, pw2=None):
    """
    Ensure passwords conform to certain standards.
    """

    import bcrypt

    if len(pw1) < 6:
      return 1, 'value specified for a password is less than 6 characters.'

    if len(pw1) < 16:
      rc =   any(pwx.islower() for pwx in pw1) and any(pwx.isupper() for pwx in pw1) and any(pwx.isnumeric() for pwx in pw1)
      if not rc:
        return 1, 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.'

    if pw2 and pw2 != pw1:
        return 1, 'values specified for passwords do not match.'


    return 0, bcrypt.hashpw(pw1.encode(), bcrypt.gensalt(prefix=b"2a"))

#-------------------------------------------------------------------------------

def verify_cloud_credentials(config, cloud):
    """
    Validate cloud credentials and, for Amazon EC2 clouds, return OwnerId.
    """

    cloud_type = None
    target_cloud = None
    auth_type = None

    if 'cloud_type' in cloud:
        cloud_type = cloud['cloud_type']
    # Must be a /cloud/update/ (not /cloud/add/) request.
    elif 'group_name' in cloud and 'cloud_name' in cloud:
        rc, msg, target_cloud = get_target_cloud(config, cloud['group_name'], cloud['cloud_name'])
        if rc == 0:
            cloud_type = target_cloud['cloud_type']
            auth_type = target_cloud.get('auth_type')
        else:
            return rc, msg, None

    if cloud_type == 'amazon':
        rc, msg, session = get_amazon_session(config, cloud, target_cloud=target_cloud)
        if rc == 0:
            try:
                return rc, msg, session.client('sts').get_caller_identity().get('Account')
            except:
                return 1, 'invalid Amazon EC2 credentials', None
        else:
            return rc, msg, None

    elif cloud_type == 'openstack':
        if cloud.get('auth_type'):
            auth_type = cloud.get('auth_type')
        if auth_type and auth_type == 'app_creds':
            rc, msg, session = get_openstack_app_creds_session(config, cloud, target_cloud=target_cloud)
        else:
            rc, msg, session = get_openstack_session(config, cloud, target_cloud=target_cloud)
        return rc, msg, None

    else:
       return 1, 'unsupported cloud_type', None

#-------------------------------------------------------------------------------

def get_target_cloud(config, group_name, cloud_name):
    table = "csv2_clouds"
    where_clause = "group_name='%s' and cloud_name='%s'" % (group_name, cloud_name)
    rc, msg, cloud_list = config.db_query(table, where=where_clause)

    if len(cloud_list) == 1:
        return 0, None, cloud_list[0]
    else:
        return 1, 'cloud %s::%s does not exist: %s' % (group_name, cloud_name, msg), None

#-------------------------------------------------------------------------------

def get_amazon_session(config, cloud, target_cloud=None):

    C = {'region': None}
    if not target_cloud and 'group_name' in cloud and 'cloud_name' in cloud:
        rc, msg, target_cloud = get_target_cloud(config, cloud['group_name'], cloud['cloud_name'])

    if target_cloud:
            C = {
                'region': target_cloud['region'],
                'aws_access_key_id': target_cloud['username'],
                'aws_secret_access_key': target_cloud['password']
                }

    if not C['region']:
        C['aws_access_key_id'] = None
        C['aws_secret_access_key'] = None

    if 'region' in cloud:
        C['region'] = cloud['region']

    if 'username' in cloud:
        C['aws_access_key_id'] = cloud['username']

    if 'password' in cloud:
        C['aws_secret_access_key'] = cloud['password']


    if C['region'] and C['aws_access_key_id'] and C['aws_secret_access_key']:
        try:
            session = boto3.session.Session(region_name=C['region'],
                aws_access_key_id=C['aws_access_key_id'],
                aws_secret_access_key=C['aws_secret_access_key'])

            return 0, None, session

        except:
            return 1, 'invalid Amazon EC2 credentials: %s' % C, None

    else:
        return 1, 'insufficient credentials to establish Amazon EC2 session: $s' % C, None

#-------------------------------------------------------------------------------

def get_openstack_app_creds_session(config, cloud, target_cloud=None):
    C = {}
    if not target_cloud and 'group_name' in cloud and 'cloud_name' in cloud:
        rc, msg, target_cloud = get_target_cloud(config, cloud['group_name'], cloud['cloud_name'])

    if target_cloud:
        if target_cloud.get('authurl'):
            C['authurl'] = target_cloud['authurl']
        if target_cloud.get('app_credentials'):
            C['app_credentials'] = target_cloud['app_credentials']
        if target_cloud.get('app_credentials_secret'):
            C['app_credentials_secret'] = target_cloud['app_credentials_secret']
        if target_cloud.get('region'):
            C['region'] = target_cloud['region']

    if 'authurl' in cloud:
        C['authurl'] = cloud['authurl']

    if 'app_credentials' in cloud:
        C['app_credentials'] = cloud['app_credentials']

    if 'app_credentials_secret' in cloud:
        C['app_credentials_secret'] = cloud['app_credentials_secret']

    if 'region' in cloud:
        C['region'] = cloud['region']

    if C.get('authurl') and C.get('app_credentials') and C.get('app_credentials_secret'):
        sess = get_openstack_sess(C, config.categories["GSI"]["cacerts"])
        if sess:
            region = None
            if C.get('region'):
                region = C['region']
            nova = get_nova_connection(sess, region)
            if nova is False:
                C.pop('app_credentials_secret')
                return 1, 'failed to get openstack connection using application credentials: %s' % C, None
            return 0, None, sess
        else:
            C.pop('app_credentials_secret')
            return 1, 'failed to esablish openstack session using application credentials: %s' % C, None
    else:
        return 1, 'Insufficient credentials to establish openstack session, check if missing any applicaion credentials info %s' % C, None

#-------------------------------------------------------------------------------

def get_openstack_session(config, cloud, target_cloud=None):
    C = {'authurl': None}
    if not target_cloud and 'group_name' in cloud and 'cloud_name' in cloud:
        rc, msg, target_cloud = get_target_cloud(config, cloud['group_name'], cloud['cloud_name'])

    if target_cloud:
        C['authurl'] = target_cloud['authurl']

    if 'authurl' in cloud:
        C['authurl'] = cloud['authurl']

    #print(">>>>>>>>>>>>>>>>>>>>>>>>>> CLOUD", cloud, "TARGET", target_cloud, "AUTHURL", C['authurl'])
    if C['authurl']:
        rc, msg, version = get_openstack_api_version(C['authurl'])
        if rc != 0:
            return rc, msg, None # could not determine version

        if version == 2:
            if target_cloud:
                C['region'] = target_cloud['region']
                C['project'] = target_cloud['project']
                C['username'] = target_cloud['username']
                C['password'] = target_cloud['password']

            else:
                C['region'] = None
                C['project'] = None
                C['username'] = None
                C['password'] = None

            if 'region' in cloud:
                C['region'] = cloud['region']

            if 'project' in cloud:
                C['project'] = cloud['project']

            if 'username' in cloud:
                C['username'] = cloud['username']

            if 'password' in cloud:
                C['password'] = cloud['password']

        elif version == 3:
            if target_cloud:
                C['region'] = target_cloud['region']
                C['project_domain_id'] = target_cloud['project_domain_id']
                C['project_domain_name'] = target_cloud['project_domain_name']
                C['project'] = target_cloud['project']
                C['user_domain_name'] = target_cloud['user_domain_name']
                C['username'] = target_cloud['username']
                C['password'] = target_cloud['password']

            else:
                C['region'] = None
                C['project_domain_id'] = None
                C['project_domain_name'] = 'Default'
                C['project'] = None
                C['user_domain_name'] = 'Default'
                C['username'] = None
                C['password'] = None

            if 'region' in cloud:
                C['region'] = cloud['region']

            if 'project_domain_id' in cloud:
                C['project_domain_id'] = cloud['project_domain_id']

            if 'project_domain_name' in cloud:
                C['project_domain_name'] = cloud['project_domain_name']

            if 'project' in cloud:
                C['project'] = cloud['project']

            if 'user_domain_name' in cloud:
                C['user_domain_name'] = cloud['user_domain_name']

            if 'username' in cloud:
                C['username'] = cloud['username']

            if 'password' in cloud:
                C['password'] = cloud['password']

    else:
        return 1, 'Missing openstack URL', None
    
    if version == 2:
        if C['authurl'] and C['region'] and C['project'] and C['username'] and C['password']:
#                KC = v2c.Client(
#                    auth_url=C['authurl'],
#                    tenant_name=C['project'],
#                    username=C['username'],
#                    password=C['password']
#                    )
            session = get_openstack_sess(C, config.categories["GSI"]["cacerts"])
            if session:
                nova = get_nova_connection(session, C['region'])
                if nova is False:
                    C.pop("password")
                    return 1, 'failed to get openstack connection using the v2 password session with credentials: %s' % C, None
                return 0, None, session
            else:
                C.pop("password") 
                return 1, 'failed to esablish openstack v2 session with credentials: %s' % C, None

        else:
            return 1, 'insufficient credentials to establish openstack v2 session, check if missed openstack url or user/project info: %s' % C, None

    elif version == 3:
        if C['authurl'] and C['region'] and C['project_domain_name'] and C['project'] and C['user_domain_name'] and C['username'] and C['password']:
#                KC = v3c.Client(
#                    auth_url=C['authurl'],
#                    project_domain_id=C['project_domain_id'],
#                    project_domain_name=C['project_domain_name'],
#                    project_name=C['project'],
#                    user_domain_name=C['user_domain_name'],
#                    username=C['username'],
#                    password=C['password']
#                    )
            session = get_openstack_sess(C, config.categories["GSI"]["cacerts"])
            if session:    
                nova = get_nova_connection(session, C['region'])
                if nova is False:
                    C.pop("password")
                    return 1, 'failed to get openstack connection using the v3 password session with credentials: %s' % C, None
                return 0, None, session
            else:
                C.pop("password")
                return 1, 'failed to esablish openstack v3 session with credentials: %s' % C, None

        else:
            return 1, 'insufficient credentials to establish openstack v3 session, check if missing any user/project info: %s' % C, None

    else:
        return 1, 'Bad openstack URL: %s, unsupported version: %s' % (target_cloud['authurl'], version), None

#-------------------------------------------------------------------------------

def get_app_credentail_expiry(cloud=None, config=None, target_cloud=None, user_id=None, app_credential_id=None, sess=None):
    C = {}
    if not target_cloud and config and cloud.get('group_name') and cloud.get('cloud_name'):
        rc, msg, target_cloud = get_target_cloud(config, cloud['group_name'], cloud['cloud_name'])
    
    if target_cloud:
        if target_cloud.get('authurl'):
            C['authurl'] = target_cloud['authurl']
        if target_cloud.get('userid'):
            C['userid'] = target_cloud['userid']
        if target_cloud.get('app_credentials'):
            C['app_credentials'] = target_cloud['app_credentials']
        if target_cloud.get('app_credentials_secret'):
            C['app_credentials_secret'] = target_cloud['app_credentials_secret']

    if cloud:
        if cloud.get('authurl'):
            C['authurl'] = cloud['authurl']
        if cloud.get('userid'):
            C['userid'] = cloud['userid']
        if cloud.get('app_credentials'):
            C['app_credentials'] = cloud['app_credentials']
        if cloud.get('app_credentials_secret'):
            C['app_credentials_secret'] = cloud['app_credentials_secret']

    if app_credential_id:
        C['app_credentials'] = app_credential_id
    if user_id:
        C['userid'] = user_id

    if not sess and C.get('authurl') and C.get('app_credentials') and C.get('app_credentials_secret'):
        verify = config.categories["GSI"]["cacerts"] if config else None
        sess = get_openstack_sess(C, verify)
    if sess:
        keystone = get_keystone_connection(sess)
        if C.get('userid') and C.get('app_credentials'):
            try:
                found_app_credential = keystone.get_application_credential(user=C['userid'], application_credential=C['app_credentials'])
                expire_date = found_app_credential['expires_at']
                if expire_date:
                    # convert to epoch time
                    datetimeObj = datetime.strptime(expire_date, '%Y-%m-%dT%H:%M:%S.%f')
                    expire_date = datetimeObj.timestamp()
                return 0, None, expire_date
            except Exception as exc:
                return 1, 'failed to get expire date of app creds %s' % exc, None
        else:
            return 1, 'Failed to get expire date of app creds, insufficient credentials to establish openstack session, check if missing userid or application credentials info: %s' % C, None
    return 1, 'Failed to get expire date of app creds, failed establish openstack session using application credentials: %s' % C, None

#-------------------------------------------------------------------------------

# This function accepts a string or a dictionary and converts any bytestrings to regular strings.
def check_convert_bytestrings(values):
    if isinstance(values, dict):
        # we have a dictionary, go thru converting byte strings
        for key in values.keys():
            if isinstance(values[key], bytes):
                values[key] = values[key].decode("utf-8")
        return values

    else:
        # it's just a single value, decode it if its a bytestring & return
        if isinstance(value, bytes):
            return values.decode("utf-8")
        else:
            return values


def retire_cloud_vms(config, group_name, cloud_name):
    VM = "csv2_vms"
    where_clause = "cloud_name='%s' and group_name='%s'" % (cloud_name, group_name)
    rc, msg, vm_list = config.db_query(VM, where=where_clause)
    for vm in vm_list:
        vm["retire"] = 1
        vm["updater"]= get_frame_info() + ":r1"
        config.db_merge(VM, vm)
    config.db_commit()
